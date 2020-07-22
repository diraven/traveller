"""Moderator tools cog module."""

from datetime import datetime

import discord
from discord.ext import commands
from discord.ext.commands import has_permissions

from core import paginators
from core.cogbase import CogBase
from core.context import Context
from extensions.mod.models import UserLog, LogRecordType


class Cog(CogBase):
    """Publicroles cog."""

    @commands.group(
        invoke_without_command=True,
    )
    @has_permissions(view_audit_log=True)
    async def mod(
            self,
            ctx: Context,
            *args: str,
    ) -> None:
        """Do nothing. At least, for now."""
        pass

    @mod.command()
    @has_permissions(view_audit_log=True)
    async def dossier(
            self,
            ctx: Context,
            member: discord.Member,
    ) -> None:
        """Attach note to the user."""
        docs = await UserLog.get(guild_id=ctx.guild.id, user_id=member.id)
        await paginators.post_from_motor(
            ctx=ctx,
            data=docs,
            title=f'{member}\'s dossier',  # noqa
            formatter=lambda x: f'**{x["type"]}** by '
                                f'<@{x.get("author_user_id", "unknown")}> \n'
                                f'{datetime.utcfromtimestamp(x["created_at"])}'
                                f'\n'
                                f'{x["text"]}\n',
        )

    @mod.command()
    @has_permissions(view_audit_log=True)
    async def note(
            self,
            ctx: Context,
            member: discord.Member,
            *,
            text: str,
    ) -> None:
        """Attach note to the user."""
        if len(text) > 128:
            await ctx.post_warning('Text is too long. 128 chars max.')
            return
        await UserLog.add_record(
            guild_id=ctx.guild.id,
            user_id=member.id,
            author_user_id=ctx.author.id,
            type_=LogRecordType.NOTE,
            text=text,
        )
        await ctx.react_ok()

    @mod.command()
    @has_permissions(view_audit_log=True)
    async def warn(
            self,
            ctx: Context,
            member: discord.Member,
            *,
            text: str,
    ) -> None:
        """Warn user."""
        if len(text) > 128:
            await ctx.post_warning('Text is too long. 128 chars max.')
            return
        await UserLog.add_record(
            guild_id=ctx.guild.id,
            user_id=member.id,
            author_user_id=ctx.author.id,
            type_=LogRecordType.WARNING,
            text=text,
        )
        await ctx.post_warning(
            f'{member} has got a warning:\n{text}',
        )

    @mod.command()
    @has_permissions(kick_members=True)
    async def kick(
            self,
            ctx: Context,
            member: discord.Member,
            *,
            text: str,
    ) -> None:
        """Kick user."""
        if len(text) > 128:
            await ctx.post_warning('Text is too long. 128 chars max.')
            return
        await UserLog.add_record(
            guild_id=ctx.guild.id,
            user_id=member.id,
            author_user_id=ctx.author.id,
            type_=LogRecordType.KICK,
            text=text,
        )
        await member.kick(reason=text)
        await ctx.post_warning(
            f'{member} has been kicked:\n{text}',
        )

    @mod.command()
    @has_permissions(ban_members=True)
    async def ban(
            self,
            ctx: Context,
            member: discord.Member,
            *,
            text: str,
    ) -> None:
        """Ban user."""
        if len(text) > 128:
            await ctx.post_warning('Text is too long. 128 chars max.')
            return
        await UserLog.add_record(
            guild_id=ctx.guild.id,
            user_id=member.id,
            type_=LogRecordType.BAN,
            author_user_id=ctx.author.id,
            text=text,
        )
        await member.ban(reason=text)
        await ctx.post_warning(
            f'{member} has been banned:\n{text}',
        )
