"""Bot testing commands module."""
from discord import Color
from discord.ext import commands

from core import CogBase, Context, EMOJI_UNICODE, Message
from core.checks import is_registered


class Cog(CogBase):
    """A set of bot testign commands."""

    @commands.group(invoke_without_command=True)
    @commands.check(is_registered)
    async def bc(self, ctx: Context):
        """General info about the character."""
        await ctx.message.add_reaction(EMOJI_UNICODE[':crab:'])

    @bc.command()
    @commands.check(is_registered)
    async def venture(self, ctx: Context) -> None:
        """Send character on to a venture."""
        await ctx.post(
            Message(
                text="nothing happened",
                # title="title",
                icon=EMOJI_UNICODE[':crab:'],
                color=Color.dark_green()),
        )
