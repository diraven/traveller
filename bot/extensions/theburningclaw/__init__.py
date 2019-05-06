"""Package with a bunch of testing commands."""
from discord.ext import commands

from .cog import Cog


def setup(bot: commands.Bot) -> None:
    """Set up bot with cog."""
    bot.add_cog(Cog(bot))
