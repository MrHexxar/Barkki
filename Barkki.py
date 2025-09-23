"""
Barkki.py -- Main entry point for Barkki.

Handles:
- Bot initialization with proper intents
- Dynamic cog loading
- Bot startup and logging
"""

import discord
from discord.ext import commands, tasks
from utils.config import Config
import importlib
import pkgutil

CONFIG = Config()

intents = discord.Intents.all()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)


async def load_command_modules():
    """
    Dynamically load all cogs in the 'commands' package.

    Looks for modules with either:
    - an async `setup(bot)` function
    - or a `Cog` subclass to register manually.

    Notes:
        - If a module has neither, we just ignore it.
    """
    import commands as commands_pkg
    for finder, name, ispkg in pkgutil.iter_modules(commands_pkg.__path__):
        module_name = f"commands.{name}"
        module = importlib.import_module(module_name)
        if hasattr(module, "setup"):
            await module.setup(bot)
        elif hasattr(module, "Cog"):
            await bot.add_cog(module.Cog(bot))


@bot.event
async def on_ready():
    """
    Event fired when the bot is ready.

    Responsibilities:
        - Load all command modules (cogs)
        - Sync slash commands with Discord
        - Print info about successful login
    """
    print(f"Logged in as {bot.user} ({bot.user.id})")
    try:
        await load_command_modules()
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} commands")
    except Exception as e:
        print(f"Failed to sync commands: {e}")


def create_and_run_bot():
    bot.run(CONFIG.token)


if __name__ == "__main__":
    create_and_run_bot()
