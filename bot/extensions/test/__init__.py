from discord.ext import commands

from .cog import Cog


def setup(bot: commands.Bot) -> None:
    bot.add_cog(Cog(bot))
