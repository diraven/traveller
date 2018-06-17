"""
Custom override for default discord.py bot implementation.
"""
from discord.ext.commands import Bot, Context

from mydiscord.commands.test import test
from mydiscord.models import Guild, Alias


class MyBot(Bot):
    """
    Custom bot override.
    """

    async def get_context(self, message, *, cls=Context) -> Context:
        """
        Returns command invocation context.
        """
        ctx = await super().get_context(message)  # type: Context

        # If command not found - try to find it using alias.
        if ctx.command is None:
            try:
                alias = Alias.objects.get(
                    guild__uid=ctx.guild.id,
                    source=ctx.invoked_with,
                )
                ctx.command = self.all_commands.get(alias.target)
            except Alias.DoesNotExist:
                pass

        return ctx


bot = MyBot('.')

bot.add_command(test)


@bot.check
def is_module_active(ctx: Context):
    """
    Checks if module is active for given guild.
    """
    return ctx.command.module.split('.')[0] in Guild.objects.get(
        uid=ctx.guild.id
    ).modules.values_list('name', flat=True)
