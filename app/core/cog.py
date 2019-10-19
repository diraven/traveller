"""Publicroles cog module."""
from discord.ext import commands

from core import utils
from core.cogbase import CogBase
from core.context import Context
from core.models import Alias


class Cog(CogBase):
    """Core cog."""

    @commands.command()
    async def about(
            self,
            ctx: Context,
    ) -> None:
        """Show information about bot developer."""
        await ctx.post_info(
            '**Developer:** DiRaven#0519 \n'
            '**Sources:** https://github.com/diraven/crabot \n',
        )

    @commands.group(invoke_without_command=True)
    @utils.is_owner_or_admin()
    async def aliases(
            self,
            ctx: Context,
    ) -> None:
        """Show configured aliases."""
        aliases = await Alias.get_by_guild(guild_id=ctx.guild.id)
        await utils.Paginator(
            ctx=ctx,
            member=ctx.author,
            items=[f'`{v["src"]}` -> `{v["dst"]}`' for v in aliases],
            separator='\n',
            title='command aliases',
        ).post()

    @aliases.command(name='set')
    @utils.is_owner_or_admin()
    async def aliases_set(
            self,
            ctx: Context,
            src: str,
            dst: str,
    ) -> None:
        """Set alias."""
        await Alias.upsert(
            guild_id=ctx.guild.id,
            src=src,
            dst=dst,
        )
        await ctx.react_ok()

    @aliases.command(name='del')
    @utils.is_owner_or_admin()
    async def aliases_del(
            self,
            ctx: Context,
            q: str,
    ) -> None:
        """Delete alias."""
        count = await Alias.delete(
            guild_id=ctx.guild.id,
            src=q,
        )
        if count:
            await ctx.react_ok()
        else:
            await ctx.post_warning('No such alias was found.')
