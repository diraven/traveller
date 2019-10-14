import Levenshtein
import discord
import typing
import asyncio
from discord.ext import commands

from core import utils
from core.cogbase import CogBase
from core.context import Context
from core.message import Message
from core.utils import escape

from extensions.administration.models import Server


class Cog(CogBase):
    """Publicroles cog."""

    @commands.group(
        invoke_without_command=True,
    )
    async def autorole(
            self,
            ctx: Context,
    ) -> None:
        """Show autorole's comands"""

    @autorole.command()
    async def switch(
            self,
            ctx: Context,
    ):
        item, checker = await Server.get_or_create(ctx.guild.id)
        if item['status'] is False:
            await Server.update_status(ctx.guild.id, True)
        else:
            await Server.update_status(ctx.guild.id, False)
        if checker:
            await ctx.channel.send(f'Autorole module enabled')
        else:
            await ctx.channel.send(f'Autorole module disabled')

    @autorole.command()
    async def setrole(
            self,
            ctx: Context,
            *,
            arg,
    ):
        await Server.get_or_create(ctx.guild.id)
        for item in ctx.guild.roles:
            if arg in item.name:
                await Server.update_role(ctx.guild.id, item.id)
                await ctx.channel.send(f'Role set')
                break

    @autorole.command()
    async def setdelay(
            self,
            ctx: Context,
            delay,
    ):
        await Server.get_or_create(ctx.guild.id)
        await Server.set_delay(ctx.guild.id, delay)

    @autorole.command()
    async def status(
            self
    ) -> None:
        return None

    @commands.Cog.listener()
    async def on_member_join(
            self,
            member,
    ):
        role = None
        result, checker = await Server.get_or_create(member.guild.id)
        if checker is False and result['status'] is True:
            for item in member.guild.roles:
                if int(result['role']) == item.id:
                    role = item
                    break
            await asyncio.sleep(float(result['delay']) * 5)
            await member.add_roles(role)
