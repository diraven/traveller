"""Administration extension package."""
from discord.ext import commands

from .cog import Cog


def setup(bot: commands.Bot) -> None:
    """Set up mod with administration functionality."""
    bot.add_cog(Cog(bot))
