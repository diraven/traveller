"""Bot testing commands module."""
from discord import Color
from discord.ext import commands

from core.cogbase import CogBase
from core.context import Context
from core.emoji import EMOJI_UNICODE
from core.message import Message


class Cog(CogBase):
    """A set of bot testign commands."""

    @commands.group()
    async def test(self, ctx: Context):
        """Bot testing functions."""
        pass

    @test.command()
    async def message(self, ctx: Context) -> None:
        """Test message-type response."""
        await ctx.post(
            Message(
                text='text',
                icon=EMOJI_UNICODE[':crab:'],
                color=Color.dark_green()),
        )

    @test.command()
    async def mention(self, ctx: Context) -> None:
        """Test mention-type response."""
        await ctx.post(
            Message(
                text='text',
                icon=EMOJI_UNICODE[':crab:'],
                color=Color.dark_green(),
            ),
            with_mention=True,
        )

    @test.command()
    async def reaction(self, ctx: Context) -> None:
        """Test reactions."""
        await ctx.message.add_reaction(EMOJI_UNICODE[':question_mark:'])
        await ctx.message.clear_reactions()
        await ctx.message.add_reaction(EMOJI_UNICODE[':OK_button:'])
