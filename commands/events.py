# commands/events.py
import os

import discord
from discord.ext import commands
from discord import app_commands
from typing import Optional
from utils.timeparse import parse_date_with_formats
from zoneinfo import ZoneInfo

class EventsCog(commands.Cog):
    def __init__(self, bot: commands.Bot, tz_name="Europe/Helsinki"):
        self.bot = bot
        self.tz_name = tz_name

    @app_commands.command(name="schedule", description="Schedule a new event")
    @app_commands.describe(location="Location", name="Name", description="Description", end="End date/time (optional)",
                           start="Start date/time (optional)")
    async def schedule(self, interaction: discord.Interaction, location: str, name: str, description: str,
                       end: Optional[str] = None, start: Optional[str] = None):
        helsinki = ZoneInfo(self.tz_name)
        from datetime import datetime, timedelta
        start_dt = datetime.now(helsinki).replace(hour=8, minute=0, second=0, microsecond=0) + timedelta(days=1)
        end_dt = datetime.now(helsinki).replace(hour=23, minute=59, second=0, microsecond=0) + timedelta(days=1)

        if end and not start:
            parsed = parse_date_with_formats(end, self.tz_name)
            if parsed is None:
                await interaction.response.send_message("End date is not valid. Please use DD-MM-YYYY or HH:MM DD.MM.YYYY format.")
                return
            end_dt = parsed
            start_dt = end_dt.replace(hour=8) - timedelta(days=1)
        elif start and not end:
            parsed = parse_date_with_formats(start, self.tz_name)
            if parsed is None:
                await interaction.response.send_message("Start date is not valid. Please use DD-MM-YYYY or HH:MM DD.MM.YYYY format.")
                return
            start_dt = parsed
            end_dt = start_dt.replace(hour=23, minute=59) + timedelta(days=1)
        elif start and end:
            parsed_s = parse_date_with_formats(start, self.tz_name)
            parsed_e = parse_date_with_formats(end, self.tz_name)
            if parsed_s is None:
                await interaction.response.send_message("Start date is not valid. Please use DD-MM-YYYY or HH:MM DD.MM.YYYY format.")
                return
            if parsed_e is None:
                await interaction.response.send_message("End date is not valid. Please use DD-MM-YYYY or HH:MM DD.MM.YYYY format.")
                return
            start_dt = parsed_s
            end_dt = parsed_e

        # ensure tz_info
        start_dt = start_dt.replace(tzinfo=helsinki)
        end_dt = end_dt.replace(tzinfo=helsinki)

        try:
            event = await interaction.guild.create_scheduled_event(  # type: ignore
                name=name,
                description=description,
                start_time=start_dt,
                end_time=end_dt,
                privacy_level=discord.PrivacyLevel.guild_only,
                entity_type=discord.EntityType.external,
                location=location
            )
            await interaction.response.send_message(f'"{event.name}" scheduled for {start_dt.isoformat(timespec="minutes")} - {end_dt.isoformat(timespec="minutes")} at {location}')
        except Exception as e:
            await interaction.response.send_message(f"Error creating event: {e}")



async def setup(bot):
    await bot.add_cog(EventsCog(bot, tz_name=os.getenv("TIMEZONE")))