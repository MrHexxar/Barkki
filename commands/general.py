"""
general.py - Basic commands for Barkki bot.
"""

import discord
from discord.ext import commands
from discord import app_commands


class GeneralCog(commands.Cog):
    # class constructor. Called when this class gets initialized.
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot  # save bot instance for later use

    # /woof command -> replies with "Woof!"
    @app_commands.command(name="woof", description="Get a happy woof")
    async def woof(self, interaction: discord.Interaction) -> None:
        await interaction.response.send_message("Woof!")

    # /help command -> shows a help text with usage instructions
    @app_commands.command(name="help", description="Detailed instructions for using commands")
    async def help(self, interaction: discord.Interaction) -> None:
        help_text = (
            "Here are the available commands:\n"
            "/woof - Get a happy woof\n\n"
            "/schedule - Schedule an event. Start defaults to 08:00, end to 23:59\n"
            "- <location> - Location of the event\n"
            "- <name> - Name of the event\n"
            "- <description> - Event description\n"
            "- <end date/time> - Format: DD-MM-YYYY or HH:MM DD.MM.YYYY\n"
            "- <start date/time> - Same format as end\n\n"
            "/chosen - Pick a random member (or from a role)\n"
            "- <role> (optional) - Restrict to a role"
        )
        await interaction.response.send_message(help_text)


# Function to load this Cog into the bot
async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(GeneralCog(bot))
