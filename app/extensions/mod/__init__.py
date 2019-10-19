"""Moderation tools extension package.."""
from discord.ext import commands

from .cog import Cog


def setup(bot: commands.Bot) -> None:
    """Set up moderation tools functionality."""
    bot.add_cog(Cog(bot))
