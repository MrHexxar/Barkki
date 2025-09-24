"""
events.py -- Cog for scheduling Discord events.
"""

import os
from datetime import datetime
import discord
from discord.ext import commands
from discord import app_commands, PrivacyLevel
from typing import Optional
from utils.timeparse import parse_date_with_formats
from zoneinfo import ZoneInfo


# Helper function that actually creates the scheduled event in Discord
async def create_event(
        interaction: discord.Interaction,
        name: str,
        description: str,
        start: datetime,
        end: datetime,
        location: str,
) -> None:
    try:
        # Ask Discord to create the scheduled event
        event = await interaction.guild.create_scheduled_event(
            name=name,
            description=description,
            start_time=start,
            end_time=end,
            privacy_level=PrivacyLevel.guild_only,  # type: ignore
            entity_type=discord.EntityType.external,
            location=location,
        )
        # Tell the user that the event was created successfully
        await interaction.response.send_message(
            f'"{event.name}" scheduled from {start.isoformat(timespec="minutes")} to {end.isoformat(timespec="minutes")} at {location}'
        )
    except Exception as e:
        # Something went wrong -> send error back to user
        await interaction.response.send_message(f"Error creating event: {e}.")


# The Cog (module) that adds the /schedule command
class EventsCog(commands.Cog):
    # class constructor. Called when this class gets initialized.
    def __init__(self, bot: commands.Bot, tz_name: str = "Europe/Helsinki") -> None:
        self.bot = bot
        self.tz_name = tz_name  # save timezone to use for parsing times

    # Parse a user-provided date string
    async def _parse_or_reply(self, interaction, s: str, kind: str) -> Optional[datetime]:
        dt = parse_date_with_formats(s, self.tz_name)
        if dt is None:
            # If user gave bad format → tell them what to use
            await interaction.response.send_message(
                f"{kind.capitalize()} date is invalid. Use HH:MM DD.MM.YYYY."
            )
        return dt

    # Make sure start < end, and start is not in the past
    async def _validate_start_end(self, interaction, start_dt: datetime, end_dt: datetime) -> bool:
        now = datetime.now(ZoneInfo(self.tz_name))
        if start_dt <= now:
            await interaction.response.send_message("Start time must be in the future.")
            return False
        if end_dt <= start_dt:
            await interaction.response.send_message("End time must be after start time.")
            return False
        return True

    # The actual slash command: /schedule
    @app_commands.command(name="schedule", description="Schedule a new event")
    @app_commands.describe(
        location="Location",
        name="Name",
        description="Description",
        start="Start date/time",
        end="End date/time"
    )
    async def schedule(
            self,
            interaction: discord.Interaction,
            location: str,
            name: str,
            description: str,
            start: str,
            end: str
    ) -> None:
        # Parse start time from user
        parsed_start = await self._parse_or_reply(interaction, start, "start")
        start_dt = parsed_start
        # Parse end time from user
        parsed_end = await self._parse_or_reply(interaction, end, "end")
        end_dt = parsed_end

        # Stop if either failed to parse
        if end_dt is None or start_dt is None:
            return

        # Attach timezone to both
        start_dt = start_dt.replace(tzinfo=ZoneInfo(self.tz_name))
        end_dt = end_dt.replace(tzinfo=ZoneInfo(self.tz_name))

        # Validate before creating
        if not await self._validate_start_end(interaction, start_dt, end_dt):
            return

        # Finally, create the event
        await create_event(interaction, name, description, start_dt, end_dt, location)


# Function Discord uses to add this Cog when bot loads
async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(EventsCog(bot, tz_name=os.getenv("TIMEZONE")))
