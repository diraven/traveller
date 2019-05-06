"""General utility checks."""
from core import Context, DB, Message


# @bot.check
# def is_module_active(ctx: Context):
#     """
#     Checks if module is active for given guild.
#     """
#     return ctx.command.module.split('.')[0] in Guild.objects.get(
#         discord_id=ctx.guild.id
#     ).modules.values_list('name', flat=True)


async def is_registered(ctx: Context):
    """Check if user is registered via discord social auth."""
    exists = await DB.get_connection().fetchrow(
        f'''SELECT 1 FROM socialaccount_socialaccount WHERE uid = $1;''',
        str(ctx.author.id),
    ) is not None
    if not exists:
        await ctx.post(Message(text=f'You are not registered!'))
    return exists
