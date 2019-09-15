"""Bot testing commands module."""
import discord
from discord import Color
from discord.ext import commands

from core import utils
from core.cogbase import CogBase
from core.context import Context
from core.emoji import EMOJI_UNICODE
from core.message import Message


class Cog(CogBase):
    """A set of owner-only commands."""

    @commands.group(name='!')
    @commands.is_owner()
    async def owner(self, ctx: Context):
        """Bot owner only commands."""
        pass

    @owner.command()
    async def guilds(self, ctx: Context) -> None:
        """Test message-type response."""
        await utils.Paginator(
            ctx=ctx,
            member=ctx.author,
            items=[
                f'`{guild.name}` (`{guild.id}`)' for guild in
                ctx.bot.guilds
            ],
            separator='\n',
            title='bot guilds',
            color=discord.Color.blue(),
        ).post()

    @owner.command()
    async def invite(
            self,
            ctx: Context,
            q: str,
    ) -> None:
        """Test mention-type response."""
        for guild in ctx.bot.guilds:
            if q.lower() in guild.name.lower():
                invite = await guild.channels[0].create_invite(
                    max_age=10,
                    max_uses=1,
                    reason='One-time invite for bot owner.',
                )
                await ctx.post(Message.info(str(invite)))
                return
        await ctx.post(Message.danger('Guild not found.'))

    @owner.group()
    async def test(self, ctx: Context):
        """Bot testing functions."""
        await ctx.ok()

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
