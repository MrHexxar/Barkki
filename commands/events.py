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
import discord
from discord.ext import commands
from discord import app_commands, PrivacyLevel
from typing import Optional
from utils.timeparse import parse_date_with_formats
from zoneinfo import ZoneInfo


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
            tz_name: Timezone name for parsing events (defaults to Helsinki because why not).
        """
        self.bot = bot
        self.tz_name = tz_name

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

        Args:
            interaction: The command interaction from Discord. 
            location: Where the event takes place (yes, text is fine, GPS not required).
            name: Event name.
            description: Event description.
            end: Optional end datetime string in DD-MM-YYYY or HH:MM DD.MM.YYYY format.
            start: Optional start datetime string in DD-MM-YYYY or HH:MM DD.MM.YYYY format.

        Notes:
            - If only `end` is provided, start defaults to 08:00 the day before.
            - If only `start` is provided, end defaults to 23:59 the day after.
            - If both are provided, we just trust the user knows what they’re doing.
        """
        from datetime import datetime, timedelta  # lazy import inside the method, but fine for readability

        helsinki = ZoneInfo(self.tz_name)

        # Default times if user is too lazy to specify anything
        start_dt = datetime.now(helsinki).replace(hour=8, minute=0, second=0, microsecond=0) + timedelta(days=1)
        end_dt = datetime.now(helsinki).replace(hour=23, minute=59, second=0, microsecond=0) + timedelta(days=1)

        if end and not start:
            parsed = parse_date_with_formats(end, self.tz_name)
            if parsed is None:
                await interaction.response.send_message(
                    "End date is not valid. Please use DD-MM-YYYY or HH:MM DD.MM.YYYY format."
                )
                return
            end_dt = parsed
            start_dt = end_dt.replace(hour=8) - timedelta(days=1)

        elif start and not end:
            parsed = parse_date_with_formats(start, self.tz_name)
            if parsed is None:
                await interaction.response.send_message(
                    "Start date is not valid. Please use DD-MM-YYYY or HH:MM DD.MM.YYYY format."
                )
                return
            start_dt = parsed
            end_dt = start_dt.replace(hour=23, minute=59) + timedelta(days=1)

        elif start and end:
            parsed_s = parse_date_with_formats(start, self.tz_name)
            parsed_e = parse_date_with_formats(end, self.tz_name)

            if parsed_s is None:
                await interaction.response.send_message(
                    "Start date is not valid. Please use DD-MM-YYYY or HH:MM DD.MM.YYYY format."
                )
                return
            if parsed_e is None:
                await interaction.response.send_message(
                    "End date is not valid. Please use DD-MM-YYYY or HH:MM DD.MM.YYYY format."
                )
                return

            start_dt = parsed_s
            end_dt = parsed_e

        # Ensure timezone information is always present (Discord LOVES doing UTC)
        start_dt = start_dt.replace(tzinfo=helsinki)
        end_dt = end_dt.replace(tzinfo=helsinki)

        try:
            event = await interaction.guild.create_scheduled_event(  # type: ignore
                name=name,
                description=description,
                start_time=start_dt,
                end_time=end_dt,
                privacy_level=PrivacyLevel.guild_only, # type: ignore Fuck you, Linter
                entity_type=discord.EntityType.external,
                location=location
            )
            await interaction.response.send_message(
                f'"{event.name}" scheduled for {start_dt.isoformat(timespec="minutes")} - {end_dt.isoformat(timespec="minutes")} at {location}'
            )
        except Exception as e:
            # The classic "catch everything and just cry" approach.
            await interaction.response.send_message(f"Error creating event: {e}")


async def setup(bot: commands.Bot) -> None:
    """
    Async entry point for loading this cog.

    Args:
        bot: The main discord.py Bot instance.

    Notes:
        - Yes, `setup` must be async. Why? Because fuck you, that's why.
    """
    await bot.add_cog(EventsCog(bot, tz_name=os.getenv("TIMEZONE")))
