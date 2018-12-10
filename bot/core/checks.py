# @bot.check
# def is_module_active(ctx: Context):
#     """
#     Checks if module is active for given guild.
#     """
#     return ctx.command.module.split('.')[0] in Guild.objects.get(
#         discord_id=ctx.guild.id
#     ).modules.values_list('name', flat=True)
