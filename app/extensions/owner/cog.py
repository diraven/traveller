"""Bot testing commands module."""
import discord
from discord.ext import commands

from core import utils
from core.cogbase import CogBase
from core.context import Context
from core.message import Message


class Cog(CogBase):
    """A set of owner-only commands."""

    @commands.group()
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
