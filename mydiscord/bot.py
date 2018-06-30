"""
Custom override for default discord.py bot implementation.
"""
import importlib
import re

from discord.ext.commands import Bot

from mydiscord.context import Context
from mydiscord.models import Guild, Alias
from project.settings import INSTALLED_APPS


class MyBot(Bot):
    """
    Custom bot override.
    """

    async def get_context(self, message, *, cls=Context) -> Context:
        """
        Returns command invocation context.
        """
        ctx = await super().get_context(message, cls=Context)  # type: Context

        # If command not found - try to find it using alias.
        if ctx.command is None:
            try:
                # Try to get alias.
                alias = Alias.objects.get(
                    guild__uid=ctx.guild.id,
                    source=ctx.invoked_with,
                )
                # Replace start of the message with the alias target.
                message.content = re.sub(
                    '^{}{}'.format(self.command_prefix, alias.source),
                    '{}{}'.format(self.command_prefix, alias.target),
                    message.content,
                )
                # Try to fetch context anew.
                ctx = await super().get_context(
                    message,
                    cls=Context,
                )
            except Alias.DoesNotExist:
                pass

        return ctx


bot = MyBot('.')

# Add all cogs to the bot.
for app in INSTALLED_APPS:
    try:
        bot.add_cog(
            importlib.import_module(  # noqa: T484
                '{}.cog'.format(app)).Cog(bot)
        )
    except ModuleNotFoundError:
        pass


@bot.check
def is_module_active(ctx: Context):
    """
    Checks if module is active for given guild.
    """
    return ctx.command.module.split('.')[0] in Guild.objects.get(
        uid=ctx.guild.id
    ).modules.values_list('name', flat=True)
