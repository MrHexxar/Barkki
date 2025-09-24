"""
config.py -- Loads settings for Barkki bot.

This file takes care of reading configuration values
(like your bot token and timezone) from environment variables.
"""

import os
from dotenv import load_dotenv  # lets us read a .env file for settings

class Config:
    """
    Configuration wrapper for the bot.

    For now, it only pulls values from environment variables.
    Later, it could be expanded to read from files or databases.
    """

    def __init__(self) -> None:
        # Load variables from .env file into environment (if present)
        load_dotenv()

        # Try to grab the bot token from environment
        # If it's not there, raise an error
        self.token: str = os.getenv("DISCORD_TOKEN") or self._missing_token()

        # Get the timezone; default to Helsinki if not set
        self.timezone: str = os.getenv("TIMEZONE", "Europe/Helsinki")

    @staticmethod
    def _missing_token() -> str:
        """
        Called when DISCORD_TOKEN is missing.

        Instead of returning a fake token, it raises an error
        because the bot literally cannot work without it.
        """
        raise RuntimeError("DISCORD_TOKEN missing in environment. Barkki can’t live like this.")
