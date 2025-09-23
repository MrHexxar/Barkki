import os
from zoneinfo import ZoneInfo

class Config:
    def __init__(self):
        self.token = os.getenv("DISCORD_TOKEN")
        self.timezone = os.getenv("TIMEZONE", "Europe/Helsinki")