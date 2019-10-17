import discord
import asyncio
from discord.ext import commands

from core.cogbase import CogBase
from core.context import Context
from core.message import Message

from extensions.autorole.models import Server


class Cog(CogBase):
    """Publicroles cog."""

    @commands.group(
        invoke_without_command=True,
    )
    async def autorole(self, ctx: Context) -> None:
        """Show autorole's comands"""
        result, checker = await Server.get_or_create(ctx.guild.id)
        embed = discord.Embed(
            title='Status of autorole function.',
            colour=discord.Colour.blue(),
        )
        role = 'Not set yet.'
        for item in ctx.guild.roles:
            if item.id == int(result['role']):
                role = item.mention
                break
        if result['status']:
            status = 'on'
        else:
            status = 'off'
        embed.add_field(name='On/off status.', value=status, inline=False)
        embed.add_field(name='Established role', value=role, inline=False)
        embed.add_field(
            name='Time delay.',
            value=result['delay'] + 'm',
            inline=False
        )
        await ctx.channel.send(embed=embed)

    @autorole.command()
    async def toggle(self, ctx: Context):
        item, checker = await Server.get_or_create(ctx.guild.id)
        if item['status'] is False:
            await Server.update_status(ctx.guild.id, True)
            await ctx.post(
                Message(
                    text='Autorole module has been enabled',
                    color=discord.Colour.blue(),
                )
            )
        else:
            await Server.update_status(ctx.guild.id, False)
            await ctx.post(
                Message(
                    text='Autorole module has been disabled',
                    color=discord.Colour.blue(),
                )
            )

    @autorole.command()
    async def setrole(self, ctx: Context, *, arg):
        await Server.get_or_create(ctx.guild.id)
        for item in ctx.guild.roles:
            if arg in item.name:
                await Server.update_role(ctx.guild.id, item.id)
                await ctx.post(
                    Message(
                        title='Role has been changed.',
                        text=f'New role is {arg}',
                        color=discord.Colour.blue()
                    )
                )
                break

    @autorole.command()
    async def setdelay(self, ctx: Context, delay):
        await Server.get_or_create(ctx.guild.id)
        await Server.set_delay(ctx.guild.id, delay)
        await ctx.post(
            Message(
                title='Delay has been changed.',
                text=f'New delay is {delay} minute(s).',
                color=discord.Colour.blue(),
            )
        )

    @commands.Cog.listener()
    async def on_member_join(self, member):
        role = None
        result, checker = await Server.get_or_create(member.guild.id)
        if checker is False and result['status'] is True:
            for item in member.guild.roles:
                if int(result['role']) == item.id:
                    role = item
                    break
            await asyncio.sleep(float(result['delay']) * 60)
            await member.add_roles(role)
