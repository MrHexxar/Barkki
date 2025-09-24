"""
randomizer.py -- Commands with randomness (picking people).
"""

import discord
from discord.ext import commands
from discord import app_commands
from typing import Optional, List
import random


class RandomizerCog(commands.Cog):
    # class constructor. Called when this class gets initialized.
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot  # keep bot reference

    # /chosen command -> picks a random guild member (optionally from a role)
    @app_commands.command(name="chosen", description="Sniffs out the true chosen")
    @app_commands.describe(role="Role to choose from (optional)")
    async def chosen(self, interaction: discord.Interaction, role: Optional[str] = None) -> None:
        guild: discord.Guild = interaction.guild

        # If role is given, find it by name
        target_role: Optional[discord.Role] = discord.utils.get(guild.roles, name=role) if role else None

        # Fetch all guild members
        guild_members: List[discord.Member] = [member async for member in guild.fetch_members(limit=None)]

        # Remove bots, and if role is given, only keep members with that role
        if role is None:
            guild_members = [m for m in guild_members if not m.bot]
        else:
            guild_members = [m for m in guild_members if not m.bot and target_role in m.roles]

        # If no members are eligible, bail out
        if not guild_members:
            await interaction.response.send_message("No eligible members found.")
            return

        # Pick one at random
        chosen: discord.Member = random.choice(guild_members)
        await interaction.response.send_message(f"I have chosen thee {chosen.mention}")


# Function to load this Cog into the bot
async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(RandomizerCog(bot))
