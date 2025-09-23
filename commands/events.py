"""
events.py -- Cog for scheduling Discord events.

This cog provides the `/schedule` slash command, which lets users
create scheduled events in the Discord server with flexible date parsing.

Highlights:
- Accepts start and/or end times in formats like `DD-MM-YYYY` or `HH:MM DD.MM.YYYY`.
- Defaults to "lazy human" mode. If you don’t provide times, it just schedules
  tomorrow from 08:00 to 23:59.
- Handles timezones (defaults to Europe/Helsinki, we love Finland).
- Wraps everything in polite error messages instead of stack traces in chat.
"""

import os
from datetime import timedelta, datetime

import discord
from discord.ext import commands
from discord import app_commands, PrivacyLevel
from typing import Optional
from utils.timeparse import parse_date_with_formats, default_start_end
from zoneinfo import ZoneInfo

async def create_event(
        interaction: discord.Interaction,
        name: str,
        description: str,
        start: datetime,
        end: datetime,
        location: str,
) -> None:
    """Create the Discord scheduled event, with snarky error messages."""
    try:
        event = await interaction.guild.create_scheduled_event(  # type: ignore
            name=name,
            description=description,
            start_time=start,
            end_time=end,
            privacy_level=PrivacyLevel.guild_only,  # type: ignore
            entity_type=discord.EntityType.external,
            location=location,
        )
        await interaction.response.send_message(
            f'"{event.name}" scheduled from {start.isoformat(timespec="minutes")} to {end.isoformat(timespec="minutes")} at {location}'
        )
    except Exception as e:
        await interaction.response.send_message(f"Error creating event: {e}. Discord hates you and me.")


class EventsCog(commands.Cog):
    """
    Cog that manages scheduling Discord server events.

    This one’s job is simple: take user input, parse dates, 
    and abuse Discord's scheduled events API until it either works or explodes.
    """

    def __init__(self, bot: commands.Bot, tz_name: str = "Europe/Helsinki") -> None:
        """
        Initialize the EventsCog.

        Args:
            bot: The main discord.py Bot instance.
            tz_name: Timezone name for all scheduled events.
        """
        self.bot = bot
        self.tz_name = tz_name

    async def _parse_or_reply(
            self, interaction: discord.Interaction, s: str, kind: str
    ) -> Optional[datetime]:
        """
        Parse a date string, reply with an error if invalid.

        Args:
            interaction: Discord interaction object.
            s: Date string from the user.
            kind: 'start' or 'end', used in error messages.

        Returns:
            Parsed datetime with tzinfo or None if invalid.
        """
        dt = parse_date_with_formats(s, self.tz_name)
        if dt is None:
            await interaction.response.send_message(
                f"{kind.capitalize()} date is invalid. Use either HH:MM DD-MM-YYYY or HH:MM DD.MM.YYYY."
            )
        return dt

    async def _validate_start_end(
        self, interaction: discord.Interaction, start_dt: datetime, end_dt: datetime
    ) -> bool:
        """
        Validate that start and end are in the future and end > start.

        Returns:
            True if valid, False (and sends a Discord message) if invalid.
        """
        now = datetime.now(ZoneInfo(self.tz_name))
        if start_dt <= now:
            await interaction.response.send_message("Start time must be in the future.")
            return False
        if end_dt <= start_dt:
            await interaction.response.send_message("End time must be after start time... how did you expect this to work?")
            return False
        return True

    @app_commands.command(name="schedule", description="Schedule a new event")
    @app_commands.describe(
        location="Location",
        name="Name",
        description="Description",
        end="End date/time (optional)",
        start="Start date/time (optional)"
    )
    async def schedule(
            self,
            interaction: discord.Interaction,
            location: str,
            name: str,
            description: str,
            end: Optional[str] = None,
            start: Optional[str] = None
    ) -> None:
        """
        Slash command: Schedule a Discord server event.

        Handles optional start/end dates with defaults and timezone.

        Args:
            interaction: The command interaction from Discord.
            location: Where the event takes place.
            name: Event name.
            description: Event description.
            end: Optional end datetime string.
            start: Optional start datetime string.
        """
        start_dt, end_dt = default_start_end(self.tz_name)

        # parse user provided dates
        if start:
            parsed_start = await self._parse_or_reply(interaction, start, "start")
            if not parsed_start:
                return
            start_dt = parsed_start
        if end:
            parsed_end = await self._parse_or_reply(interaction, end, "end")
            if not parsed_end:
                return
            end_dt = parsed_end

        # fill missing dates if only one is provided
        if end and not start:
            start_dt = end_dt.replace(hour=8) - timedelta(days=1)
        if start and not end:
            end_dt = start_dt.replace(hour=23, minute=59)

        start_dt = start_dt.replace(tzinfo=ZoneInfo(self.tz_name))
        end_dt = end_dt.replace(tzinfo=ZoneInfo(self.tz_name))

        if not await self._validate_start_end(interaction, start_dt, end_dt):
            return

        await create_event(interaction, name, description, start_dt, end_dt, location)

async def setup(bot: commands.Bot) -> None:
    """
    Async entry point for loading this cog.

    Args:
        bot: The main discord.py Bot instance.

    Notes:
        - Yes, `setup` must be async. Why? Because fuck you, that's why.
    """
    await bot.add_cog(EventsCog(bot, tz_name=os.getenv("TIMEZONE")))
