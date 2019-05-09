"""Bot testing commands module."""
from discord import Color
from discord.ext import commands

from core.cogbase import CogBase
from core.context import Context
from core.emoji import EMOJI_UNICODE
from core.message import Message


class Cog(CogBase):
    """A set of bot testign commands."""

    @commands.group(invoke_without_command=True)
    async def bc(self, ctx: Context):
        """General info about the character."""
        await ctx.message.add_reaction(EMOJI_UNICODE[':crab:'])

    @bc.command()
    async def venture(self, ctx: Context) -> None:
        """Send character on to a venture."""
        await ctx.post(
            Message(
                text="nothing happened",
                # title="title",
                icon=EMOJI_UNICODE[':crab:'],
                color=Color.dark_green()),
        )
