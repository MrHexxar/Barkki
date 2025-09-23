# commands/randomizer.py
import discord
from discord.ext import commands
from discord import app_commands
from typing import Optional
import random

class RandomizerCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="chosen", description="Sniffs out the true chosen")
    @app_commands.describe(role="Role to choose from (optional)")
    async def chosen(self, interaction: discord.Interaction, role: Optional[str]=None):
        guild = interaction.guild
        target_role = discord.utils.get(guild.roles, name=role) if role else None

        # fetch members (note: fetch_members requires certain intents/permissions)
        guild_members = [member async for member in guild.fetch_members(limit=None)]
        if role is None:
            guild_members = [m for m in guild_members if not m.bot]
        else:
            guild_members = [m for m in guild_members if not m.bot and target_role in m.roles]

        if not guild_members:
            await interaction.response.send_message("No eligible members found.")
            msg = await interaction.original_response()
            await self.tracker.register_message(msg, kind="transient", meta={"cmd": "chosen"})
            return

        chosen = random.choice(guild_members)
        await interaction.response.send_message(f"I have chosen thee {chosen.mention}")

async def setup(bot):
    await bot.add_cog(RandomizerCog(bot))
