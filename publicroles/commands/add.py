from discord.ext import commands
from discord.ext.commands import Context


@commands.command()
async def add(ctx: Context, arg) -> None:
    """
    Command to add public role.
    """
    await ctx.send(arg)
