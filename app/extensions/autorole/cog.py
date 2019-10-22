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
        embed = discord.Embed(
            title='Status of autorole function.',
            colour=discord.Colour.blue(),
        )
        role = 'Not set yet.'
        delay = 'Not set yet'
        if result:
            try:
                delay = result['delay']
            except KeyError:
                delay = 'Not set yet'
            for item in ctx.guild.roles:
                if item.id == int(result['role']):
                    role = item.mention
                    break
            status = 'Online'
        else:
            status = 'Offline'
        embed.add_field(name='On/off status.', value=status, inline=False)
        embed.add_field(name='Established role.', value=role, inline=False)
        embed.add_field(
            name='Time delay in minutes.',
            value=str(delay),
            inline=False,
        )
        await ctx.channel.send(embed=embed)

    @autorole.command()
    @utils.is_owner_or_admin()
    async def shutdown(self, ctx: Context):
        """Shutdown of work autorole module."""
        await Autorole.guild_delete(ctx.guild.id)
        await ctx.post_info('Autorole module is offline.')

    @autorole.command()
    @utils.is_owner_or_admin()
    async def setrole(self, ctx: Context, *, arg):
        """Set role for autorole module."""
        for item in ctx.guild.roles:
            if arg in item.name:
                await Autorole.update_role(ctx.guild.id, item.id)
                await ctx.post_info(
                    f'**Role has been changed**.\n'
                    f'New role is {arg}.',
                )
                break
        else:
            await ctx.post_error(
                text='The role is set incorrectly.',
            )

    @autorole.command()
    @utils.is_owner_or_admin()
    async def setdelay(self, ctx: Context, delay: float):
        """Set delay for autorole module."""
        await Autorole.get(ctx.guild.id)
        await Autorole.set_delay(ctx.guild.id, float(delay))
        await ctx.post_info(
            f'**Delay has been changed.**\n '
            f'New delay is {delay} minute(s).',
        )

    @commands.Cog.listener()
    async def on_member_join(self, member):
        """Event that occurs after the user joins."""
        result = await Autorole.get(member.guild.id)
        if result:
            for item in member.guild.roles:
                if int(result['role']) == item.id:
                    role = item
                    await asyncio.sleep(float(result['delay']) * 60)
                    await member.add_roles(role)
                    break
