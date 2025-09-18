import discord
from discord.ext import commands
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo
import os
from dotenv import load_dotenv

# Setup
load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
intents = discord.Intents.default()
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
@discord.app_commands.describe(location="Location", name="Name", description="Misc information", end="End date/time (DD-MM-YYYY)", )

async def schedule(interaction: discord.Interaction, location: str, name: str, description: str, end: str):
    # Parse end date
    end_dt = datetime.strptime(end, "%d-%m-%Y")
    end_dt = end_dt.replace(hour=23, minute=59)
    # Set timezone to UTC+2
    helsinki = ZoneInfo('Europe/Helsinki')
    end_dt = end_dt.replace(tzinfo=helsinki)
    # Calculate start date (1 day before end date at 08:00)
    start_dt = end_dt - timedelta(days=1)
    start_dt = start_dt.replace(hour=8, minute=0)
    # Create the event
    event = await interaction.guild.create_scheduled_event( # type=ignore
        name=name,
        description=description,
        start_time=start_dt,
        end_time=end_dt,
        privacy_level=discord.PrivacyLevel.guild_only,
        entity_type=discord.EntityType.external,
        location=location
    )
    # Confirm to user
    await interaction.response.send_message(f"Event {event.name} scheduled until {end}")

# Run the bot
bot.run(TOKEN)