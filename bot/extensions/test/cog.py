from discord import Color
from discord.ext import commands

from bot.core import Context, CogBase, Message


class Cog(CogBase):
    @commands.group(invoke_without_command=True)
    async def test(self, ctx: Context):
        await ctx.r_acknowledge()

    @test.command()
    async def message(self, ctx: Context) -> None:
        """Responds with "pong"."""
        await ctx.post(
            Message("text", "title", "icon", Color.dark_green()),
        )

    @test.command()
    async def mention(self, ctx: Context) -> None:
        """Responds with "pong"."""
        await ctx.post(
            Message("text", "title", "icon", Color.dark_green()),
            with_mention=True,
        )

    @test.command()
    async def reactions(self, ctx: Context) -> None:
        """Responds with "pong"."""
        await ctx.r_acknowledge()
        await ctx.message.clear_reactions()
        await ctx.r_done()
