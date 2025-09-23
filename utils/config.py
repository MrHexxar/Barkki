"""
config.py -- Tiny config handler because humans forget environment variables.

Loads essential settings from the environment:
- DISCORD_TOKEN: required for Barkki to log in.
- TIMEZONE: optional, defaults to Europe/Helsinki.
"""

import os
from dotenv import load_dotenv

class Config:
    """
    Holds configuration for the bot.

    Currently, wraps environment variables. Future-proof for fancy config files should the need arise.
    """

    def __init__(self) -> None:
        """
        Initialize the Config object.

        Raises:
            RuntimeError: If DISCORD_TOKEN is missing, because Barkki can’t work without it.

        Attributes:
            token (str): Discord bot token from environment.
            timezone (str): Timezone name, defaults to "Europe/Helsinki".
        """
        load_dotenv()
        self.token: str = os.getenv("DISCORD_TOKEN") or self._missing_token()
        self.timezone: str = os.getenv("TIMEZONE", "Europe/Helsinki")

    @staticmethod
    def _missing_token() -> str:
        """Raise an exception if DISCORD_TOKEN is missing."""
        raise RuntimeError("DISCORD_TOKEN missing in environment. Barkki can’t live like this.")
