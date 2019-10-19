"""Moderator tools cog module."""

from datetime import datetime

import discord
from discord.ext import commands
from discord.ext.commands import has_permissions

from core import utils
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
    async def dossier(
            self,
            ctx: Context,
            user: discord.User,
    ) -> None:
        """Attach note to the user."""
        records = await UserLog.get(guild_id=ctx.guild.id, user_id=user.id)
        await utils.Paginator(
            ctx=ctx,
            member=ctx.author,
            items=[f'**{r["type"]}** @ '
                   f'{datetime.utcfromtimestamp(r["created_at"])}:'
                   f'\n{r["text"]}' for r in records],
            separator='\n',
            title=f'{user}\'s dossier',  # noqa
        ).post()
