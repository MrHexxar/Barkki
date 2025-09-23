import os
import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv
from utils.config import Config
import importlib
import pkgutil

load_dotenv()

CONFIG = Config()

intents = discord.Intents.all()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)
# dynamic cog loader (loads commands package modules that provide a setup function / Cog)
async def load_command_modules():
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
    print(f"Logged in as {bot.user} ({bot.user.id})")
    try:
        await load_command_modules()
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} commands")
    except Exception as e:
        print(f"Failed to sync commands: {e}")

def create_and_run_bot():
    # load command modules
    token = os.getenv("DISCORD_TOKEN")
    if token is None:
        raise RuntimeError("DISCORD_TOKEN missing in environment")
    bot.run(token)
