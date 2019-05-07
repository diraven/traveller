"""General utility checks."""
from discord.ext.commands import CommandError

from core import Context


# @bot.check
# def is_module_active(ctx: Context):
#     """
#     Checks if module is active for given guild.
#     """
#     return ctx.command.module.split('.')[0] in Guild.objects.get(
#         discord_id=ctx.guild.id
#     ).modules.values_list('name', flat=True)


async def has_socialaccount(ctx: Context):
    """Check if user is registered via discord social auth."""
    if ctx.socialaccount:
        return True
    raise CommandError('User is not registered.')
