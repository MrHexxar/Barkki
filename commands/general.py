"""
general.py - Basic commands that make Barkki feel alive.

This cog provides general utility commands like `/woof` and `/help`. 
Mostly harmless, but occasionally will make you smile (or groan).
"""

import discord
from discord.ext import commands
from discord import app_commands


class GeneralCog(commands.Cog):
    """
    General utility cog.

    Contains simple, non-event-related commands. 
    Currently includes:
    - /woof: a happy doggo sound
    - /help: instructions for using other commands
    """

    def __init__(self, bot: commands.Bot) -> None:
        """
        Initialize the GeneralCog.

        Args:
            bot: The main discord.py Bot instance.
        """
        self.bot = bot

    @app_commands.command(name="woof", description="Get a happy woof")
    async def woof(self, interaction: discord.Interaction) -> None:
        """
        Sends a cheerful 'Woof!' message.

        Args:
            interaction: The Discord interaction that triggered the command.

        Notes:
            - Truly the height of sophistication.
            - Users may request multiple woofs; your server may become a kennel.
        """
        await interaction.response.send_message("Woof!")

    @app_commands.command(name="help", description="Detailed instructions for using commands")
    async def help(self, interaction: discord.Interaction) -> None:
        """
        Sends a help message listing all available commands.

        Args:
            interaction: The Discord interaction that triggered the command.

        Notes:
            - Clearly written for humans who can't figure out `/woof`.
            - Future-proof for more commands; just expand the string.
        """
        help_text = (
            "Here are the available commands:\n"
            "/woof - Get a happy woof\n\n"
            "/schedule - Schedule an event. The start and end will default to a relevant time at 08:00 for start and 23:59 for end\n"
            "- <location> - Location of the event\n"
            "- <name> - Name of the event\n"
            "- <description> - Description for the event\n"
            "- <end date/time> (optional) - When the event starts : DD-MM-YYYY or HH:MM DD.MM.YYYY\n"
            "- <start date/time> (optional) - When the event ends : DD-MM-YYYY or HH:MM DD.MM.YYYY\n\n"
            "/chosen - Sniffs out the true chosen from all members or from a specified role\n"
            "- <role> (optional) - Role from which to pick the chosen"
        )
        await interaction.response.send_message(help_text)


async def setup(bot: commands.Bot) -> None:
    """
    Async entry point for loading this cog.

    Args:
        bot: The main discord.py Bot instance.

    Notes:
        - Yes, `setup` must be async. Why? Because fuck you, that's why.
    """
    await bot.add_cog(GeneralCog(bot))
