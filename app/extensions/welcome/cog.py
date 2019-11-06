"""Welcome message cog module."""
from discord.ext import commands

from core.cogbase import CogBase
from core.context import Context
from core import utils

from extensions.welcome.models import Welcome


class Cog(CogBase):
    """Welcome message cog."""

    @commands.group(invoke_without_command=True)
    async def welcome(self, ctx: Context) -> None:
        """Do nothing."""
        pass

    @welcome.command()
    @utils.is_owner_or_admin()
    async def setup(self, ctx: Context, *, text: str):
        """Set message fpr welcome module."""
        await Welcome.add(ctx.guild.id, text)
        await ctx.post_info('Welcome message is successfully set')

    @welcome.command()
    @utils.is_owner_or_admin()
    async def test(self, ctx: Context):
        """Show welcome message in your privat chat."""
        result = await Welcome.get(ctx.guild.id)
        try:
            await ctx.author.send(result['message'])
        except TypeError:
            await ctx.post_error('Nothing to test')

    @welcome.command()
    @utils.is_owner_or_admin()
    async def disable(self, ctx: Context):
        """Disable welcome message module."""
        await Welcome.delete(ctx.guild.id)
        await ctx.post_info('Welcome module was disabled.')

    @commands.Cog.listener()
    async def on_member_join(self, member):
        """Event that occurs after the user joins."""
        result = await Welcome.get(member.guild.id)
        await member.send(result['message'])
