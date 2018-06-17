from discord.ext import commands

from mydiscord.context import Context
from mydiscord.message import Message


class Cog:
    @commands.group(invoke_without_command=True)
    async def ping(self, ctx: Context) -> None:
        pass
        await ctx.post(Message('pong'))

    @ping.command()
    async def test(self, ctx: Context) -> None:
        await ctx.post(Message.danger('tost'))
