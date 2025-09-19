import discord
import os
import random
from discord.ext import commands
from datetime import datetime, timedelta, timezone
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

# Schedule command
@bot.tree.command(name="schedule", description="Schedule a new event")
@discord.app_commands.describe(location="Location", name="Name", description="Misc information", end="End date/time (DD-MM-YYYY or DD.MM.YYYY)")
async def schedule(interaction: discord.Interaction, location: str, name: str, description: str, end: str):
    date_formats = ["%d-%m-%Y", "%d.%m.%Y"]
    for fmt in date_formats:
        try:
            end_dt = datetime.strptime(end, fmt)
            break
        except ValueError:
            continue
    else:
        await interaction.response.send_message(
            "Invalid date! Please use DD-MM-YYYY or DD.MM.YYYY"
        )
        return

    # Parse end date
    end_dt = end_dt.replace(hour=23, minute=59)

    # Set timezone to EEST
    try:
        helsinki = ZoneInfo("Europe/Helsinki")
    except Exception as e:
        await interaction.response.send_message(
            f"Error loading timezone: {e}"
        )
        return

    end_dt = end_dt.replace(tzinfo=helsinki)
    # Calculate start date (8:00 AM same day)
    start_dt = end_dt.replace(hour=8, minute=0)
    # Create the event
    event = await interaction.guild.create_scheduled_event( # type: ignore
        name=name,
        description=description,
        start_time=start_dt,
        end_time=end_dt,
        privacy_level=discord.PrivacyLevel.guild_only,
        entity_type=discord.EntityType.external,
        location=location
    )
    # Confirm to user
    await interaction.response.send_message(f'Event "{event.name}" scheduled until {end}')

# Chosen command
@bot.tree.command(name="chosen", description="Sniffs out the true chosen")
@discord.app_commands.describe(role="Role to choose from (optional)")
async def chosen(interaction: discord.Interaction, role: Optional[str]):
    # Creating list of members
    guild = interaction.guild
    target_role = discord.utils.get(guild.roles, name=role)

    # Removes bots and members without the specified role
    guild_members = [member async for member in guild.fetch_members()]
    if role is None:
        guild_members = [member for member in guild_members if not member.bot]
    else:
        guild_members = [member for member in guild_members if not member.bot and target_role in member.roles]

    # Choose one randomly
    chosen = random.choice(guild_members)
    # Send the chosen one a message
    await interaction.response.send_message(f"The great Barkki has chosen thee {chosen.mention}")
    await chosen.send("You are chosen by Barkki!")

# Run the bot
bot.run(TOKEN)