import discord
import os
import random
from datetime import datetime, timedelta
from discord.ext import commands
from zoneinfo import ZoneInfo
from typing import Optional
from dotenv import load_dotenv

# Setup
load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
intents = discord.Intents.all()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Host information
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name} ({bot.user.id})")
    try:
        synced = await bot.tree.sync() 
        print(f"Synced {len(synced)} slash command(s)")
    except Exception as e:
        print(f"Failed syncing commands: {e}")

# Woof command
@bot.tree.command(name="woof", description="Get a happy woof")
async def woof(interaction: discord.Interaction):
    await interaction.response.send_message("Woof!")

# Help command
@bot.tree.command(name="help", description="Detailed instructions for using commands")
async def help(interaction: discord.Interaction):
    help_text = (
        "Here are the available commands:\n"
        "/woof - Get a happy woof\n\n"
        "/schedule - Schedule an event. The start and end will default to a relevant time at 08:00 for start and 23:59 for end\n"
        "- <location> - Location of the event\n"
        "- <name> - Name of the event\n"
        "- <description> - Description for the event\n"
        "- <end date/time> (optional) - When the event starts : DD-MM-YYYY or HH:MM DD.MM.YYYY\n"
        "- <start date/time> (optional) - When the event ends : DD-MM-YYYY or HH:MM DD.MM.YYYY\n\n"
        "/chosen - Sniffs out the true chosen from all members or from a specified role\n"
        "- <role> (optional) - Role from which to pick the chosen"
    )
    await interaction.response.send_message(help_text)

# Schedule command
@bot.tree.command(name="schedule", description="Schedule a new event")
@discord.app_commands.describe(location="Location", name="Name", description="Description", end="End date/time (optional)", start="Start date/time (optional)")
async def schedule(interaction: discord.Interaction, location: str, name: str, description: str, end: Optional[str], start: Optional[str]):
    # Get Helsinki timezone
    try:
        helsinki = ZoneInfo("Europe/Helsinki")
    except Exception as e:
        await interaction.response.send_message(f"Error loading timezone: {e}")
        return
    # Create default datetime objects : This is also used to ensure hours do not default to 00:00 when none are provided
    start_dt = datetime.now().replace(hour=8, minute=0) + timedelta(days=1)
    end_dt = datetime.now().replace(hour=23, minute=59) + timedelta(days=1)
    date_formats = ["%d-%m-%Y", "%H:%M %d.%m.%Y"]
    # Parse with end date
    if end and not start:
        for fmt in date_formats:
            try:
                end_dt = datetime.strptime(end, fmt)
                break
            except ValueError:
                continue
        else:
            await interaction.response.send_message("End date is not valid. Please use DD-MM-YYYY or HH:MM DD.MM.YYYY format.")
            return
        start_dt = end_dt.replace(hour=8) - timedelta(days=1)
    # Parse with start date
    elif start and not end:
        for fmt in date_formats:
            try:
                start_dt = datetime.strptime(start, fmt)
                break
            except ValueError:
                continue
        else:
            await interaction.response.send_message("Start date is not valid. Please use DD-MM-YYYY or HH:MM DD.MM.YYYY format.")
            return
        end_dt = start_dt.replace(hour=23, minute=59) + timedelta(days=1)
    # Parse with both dates
    elif start and end:
        for fmt in date_formats:
            try:
                start_dt = datetime.strptime(start, fmt)
                break
            except ValueError:
                continue
        else:
            await interaction.response.send_message("Start date is not valid. Please use DD-MM-YYYY or HH:MM DD.MM.YYYY format.")
            return
        for fmt in date_formats:
            try:
                end_dt = datetime.strptime(end, fmt)
                break
            except ValueError:
                continue
        else:
            await interaction.response.send_message("End date is not valid. Please use DD-MM-YYYY or HH:MM DD.MM.YYYY format.")
            return
    # Ensure timezone
    end_dt = end_dt.replace(tzinfo=helsinki)
    start_dt = start_dt.replace(tzinfo=helsinki)
    # Create the event
    try:
        event = await interaction.guild.create_scheduled_event( # type: ignore
            name=name,
            description=description,
            start_time=start_dt,
            end_time=end_dt,
            privacy_level=discord.PrivacyLevel.guild_only,
            entity_type=discord.EntityType.external,
            location=location
        )
        await interaction.response.send_message(f'"{event.name}" scheduled for {start_dt.isoformat("/", "minutes")} - {end_dt.isoformat("/", "minutes")} at {location}')
    except Exception:
        await interaction.response.send_message(f"Error creating event, please ensure that all inputs are valid. {start_dt} - {end_dt}")
        return

# Chosen command
@bot.tree.command(name="chosen", description="Sniffs out the true chosen")
@discord.app_commands.describe(role="Role to choose from (optional)")
async def chosen(interaction: discord.Interaction, role: Optional[str]):
    # Setup
    guild = interaction.guild
    target_role = discord.utils.get(guild.roles, name=role)

    # Creates list of members to choose from, excluding bots and filtering roles if specified
    guild_members = [member async for member in guild.fetch_members()]
    if role is None:
        guild_members = [member for member in guild_members if not member.bot]
    else:
        guild_members = [member for member in guild_members if not member.bot and target_role in member.roles]

    # Chooses one randomly from the list of available members
    chosen = random.choice(guild_members)
    # Send the chosen one a message
    await interaction.response.send_message(f"I have chosen thee {chosen.mention}")

# Run the bot
bot.run(TOKEN)