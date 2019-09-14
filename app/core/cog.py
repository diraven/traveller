"""Publicroles cog module."""
import discord
from discord.ext import commands

from core import utils
from core.cogbase import CogBase
from core.context import Context
from core.message import Message
from core.models import Guild


class Cog(CogBase):
    """Core cog."""

    @commands.group(invoke_without_command=True)
    @commands.has_permissions(administrator=True)
    async def alias(
            self,
            ctx: Context,
            *args: str,
    ) -> None:
        """Show available aliases."""
        guild, _ = await Guild.get_or_create(ctx.guild.id)
        await utils.Paginator(
            ctx=ctx,
            member=ctx.author,
            items=[
                f'`{v["src"]}` -> `{v["dst"]}`' for v in
                guild.get('aliases', {})
            ],
            separator='\n',
            title='command aliases',
            color=discord.Color.blue(),
        ).post()

    @alias.command(name='add')
    async def add_alias(
            self,
            ctx: Context,
            *args: str,
    ) -> None:
        """Add new alias."""
        if len(args) != 2:
            await ctx.post(Message.danger(
                'Exactly 2 parameters must be provided for this command.',
            ))
            return
        count = await Guild.add_alias(
            guild_id=ctx.guild.id,
            src=args[0],
            dst=args[1],
        )
        if count:
            await ctx.ok()
        else:
            await ctx.post(Message.danger(
                'Such alias already exists.',
            ))

    @alias.command(name='del')
    async def del_alias(
            self,
            ctx: Context,
            *args: str,
    ) -> None:
        """Delete alias."""
        if len(args) != 1:
            await ctx.post(Message.danger(
                'Exactly 1 parameters must be provided for this command.',
            ))
            return
        count = await Guild.del_alias(
            guild_id=ctx.guild.id,
            src=args[0],
        )
        if count:
            await ctx.ok()
        else:
            await ctx.post(Message.danger(
                'No such alias was found.',
            ))
