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
            user: discord.User,
    ) -> None:
        """Attach note to the user."""
        docs = await UserLog.get(guild_id=ctx.guild.id, user_id=user.id)
        await paginators.post_from_motor(
            ctx=ctx,
            data=docs,
            title=f'{user}\'s dossier',  # noqa
            formatter=lambda x: f'**{x["type"]}** @ '
                                f'{datetime.utcfromtimestamp(x["created_at"])}'
                                f'\n'
                                f'{x["text"]}\n',
        )

    @mod.command()
    @has_permissions(view_audit_log=True)
    async def note(
            self,
            ctx: Context,
            user: discord.User,
            *,
            text: str,
    ) -> None:
        """Attach note to the user."""
        if len(text) > 128:
            await ctx.post_warning('Text is too long. 128 chars max.')
            return
        await UserLog.add_record(
            guild_id=ctx.guild.id,
            user_id=user.id,
            type_=LogRecordType.NOTE,
            text=text,
        )
        await ctx.react_ok()

    @mod.command()
    @has_permissions(view_audit_log=True)
    async def warn(
            self,
            ctx: Context,
            user: discord.User,
            *,
            text: str,
    ) -> None:
        """Attach note to the user."""
        if len(text) > 128:
            await ctx.post_warning('Text is too long. 128 chars max.')
            return
        await UserLog.add_record(
            guild_id=ctx.guild.id,
            user_id=user.id,
            type_=LogRecordType.WARNING,
            text=text,
        )
        await ctx.post_warning(
            f'{user} has got a warning:\n{text}',
        )
