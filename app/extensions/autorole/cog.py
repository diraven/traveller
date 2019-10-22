"""Autorole cog module."""
import discord
import asyncio
from discord.ext import commands

from core.cogbase import CogBase
from core.context import Context
from core import utils

from extensions.autorole.models import Autorole


class Cog(CogBase):
    """Publicroles cog."""

    @commands.group(invoke_without_command=True)
    async def autorole(self, ctx: Context) -> None:
        """Show autorole's status."""
        result = await Autorole.get(ctx.guild.id)
        if result:
            delay = result['delay']
            role = ctx.guild.get_role(result['role_id'])
            try:
                await ctx.post_info(f'{role.mention} with {delay}m delay.')
            except AttributeError:
                await Autorole.delete(ctx.guild.id)
        else:
            await ctx.post_info(f'Not set.')

    @autorole.command()
    @utils.is_owner_or_admin()
    async def disable(self, ctx: Context):
        """Shutdown of work autorole module."""
        await Autorole.delete(ctx.guild.id)
        await ctx.post_info('Autorole disabled.')

    @autorole.command()
    @utils.is_owner_or_admin()
    async def set(self, ctx: Context, role: discord.Role, delay: float):
        """Set role for autorole module."""
        if delay < 0:
            await ctx.post_error(
                'Delay format is incorrect.'
            )
        elif delay > 40:
            await ctx.post_error(
                'Delay is too big.'
            )
        else:
            await Autorole.set(ctx.guild.id, role.id, float(delay))
            await ctx.post_info(
                f'Autorole was set to {role.mention} '
                f'with {delay} minute(s) delay.',
            )

    @commands.Cog.listener()
    async def on_member_join(self, member):
        """Event that occurs after the user joins."""
        result = await Autorole.get(member.guild.id)
        if result:
            role = member.guild.get_role(result['role_id'])
            if role:
                await asyncio.sleep(float(result['delay']) * 60)
                await member.add_roles(role)
            else:
                await Autorole.delete(member.guild.id)
