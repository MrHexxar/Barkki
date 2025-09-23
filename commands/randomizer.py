"""
randomizer.py -- Pick the lucky (or unlucky) soul.

This cog provides commands that involve randomness. Currently just `/chosen`:
- Selects a member from the guild (optionally filtered by role)
- Excludes bots because yes, bots don’t get a say
- Randomly assigns fate with zero remorse
"""

import discord
from discord.ext import commands
from discord import app_commands
from typing import Optional, List
import random


class RandomizerCog(commands.Cog):
    """
    Randomness-related commands.

    Right now, it’s just the `/chosen` command:
    pick a member and publicly shame... I mean, honor them.
    """

    def __init__(self, bot: commands.Bot) -> None:
        """
        Initialize the RandomizerCog.

        Args:
            bot: The main discord.py Bot instance.
        """
        self.bot = bot

    @app_commands.command(name="chosen", description="Sniffs out the true chosen")
    @app_commands.describe(role="Role to choose from (optional)")
    async def chosen(self, interaction: discord.Interaction, role: Optional[str] = None) -> None:
        """
        Randomly pick a member from the guild (or a specified role).

        Args:
            interaction: The Discord interaction that triggered the command.
            role: Optional role to restrict the pool of eligible members.

        Notes:
            - Bots are excluded from selection because they don’t deserve it.
            - Requires `members` intent to fetch the full member list.
            - If no eligible members exist, politely informs the user.
        """
        guild: discord.Guild = interaction.guild
        target_role: Optional[discord.Role] = discord.utils.get(guild.roles, name=role) if role else None

        guild_members: List[discord.Member] = [member async for member in guild.fetch_members(limit=None)]

        # Filter out bots, optionally filter by role
        if role is None:
            guild_members = [m for m in guild_members if not m.bot]
        else:
            guild_members = [m for m in guild_members if not m.bot and target_role in m.roles]

        if not guild_members:
            await interaction.response.send_message("No eligible members found.")
            return

        chosen: discord.Member = random.choice(guild_members)
        await interaction.response.send_message(f"I have chosen thee {chosen.mention}")


async def setup(bot: commands.Bot) -> None:
    """
    Async entry point for loading this cog.

    Args:
        bot: The main discord.py Bot instance.

    Notes:
        - Yes, `setup` must be async. Why? Because fuck you, that's why.
    """
    await bot.add_cog(RandomizerCog(bot))
