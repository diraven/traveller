"""Eve killmail extension package."""
from discord.ext import commands

from .cog import Cog


def setup(bot: commands.Bot) -> None:
    """Set up mod for eve killmain."""
    bot.add_cog(Cog(bot))