from discord.ext import commands

from mydiscord.cogbase import CogBase
from mydiscord.context import Context
from mydiscord.message import Message


class Cog(CogBase):
    @commands.group(invoke_without_command=True)
    async def test(self, ctx: Context) -> None:
        await ctx.acknowledge()

    @test.command()
    async def ping(self, ctx: Context) -> None:
        await ctx.post(Message('pong'))
