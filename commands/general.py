import discord
from discord.ext import commands
from discord import app_commands
from typing import Optional

class GeneralCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="woof", description="Get a happy woof")
    async def woof(self, interaction: discord.Interaction):
        await interaction.response.send_message("Woof!")

    @app_commands.command(name="help", description="Detailed instructions for using commands")
    async def help(self, interaction: discord.Interaction):
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


async def setup(bot):
    await bot.add_cog(GeneralCog(bot))