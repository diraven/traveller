from discord.ext import commands
from discord.ext.commands import Context


@commands.command()
async def test(ctx: Context, arg) -> None:
    """
    Basic test command.
    """
    await ctx.send(arg)
