"""Bot testing commands module."""
from discord.ext import commands

from core import paginators
from core.cogbase import CogBase
from core.context import Context
from core.emoji import EMOJI_UNICODE


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
        await paginators.List(
            ctx=ctx,
            items=[
                f'`{guild.name}` (`{guild.id}`)' for guild in
                ctx.bot.guilds
            ],
            title='bot guilds',
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
                await ctx.post_info(str(invite))
                return
        await ctx.post_warning('Guild not found.')

    @owner.group()
    async def test(self, ctx: Context):
        """Bot testing functions."""
        await ctx.react_ok()

    @test.command()
    async def message(self, ctx: Context) -> None:
        """Test message-type response."""
        await ctx.post_info(
            text='Test message.',
        )

    @test.command()
    async def reaction(self, ctx: Context) -> None:
        """Test reactions."""
        await ctx.message.add_reaction(EMOJI_UNICODE[':question_mark:'])
        await ctx.message.clear_reactions()
        await ctx.message.add_reaction(EMOJI_UNICODE[':OK_button:'])
