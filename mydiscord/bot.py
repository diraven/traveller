"""
Custom override for default discord.py bot implementation.
"""
import importlib
import re

from discord.ext.commands import Bot, CheckFailure, CommandNotFound, \
    MissingRequiredArgument

from mydiscord.context import Context
from mydiscord.message import Message
from mydiscord.models import Guild, Alias
from project.settings import INSTALLED_APPS, RAVEN_CONFIG


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

    # noinspection PyBroadException
    async def on_command_error(self, ctx: Context, error) -> None:
        """
        Global command errors handler.
        """
        # Ignore checks failures.
        if isinstance(error, CheckFailure) or isinstance(error,
                                                         CommandNotFound):
            return

        # Process missing command arguments error by responding to the user.
        if isinstance(error, MissingRequiredArgument):
            await ctx.post(
                Message.danger(
                    "Incorrect command usage, missing argument. "
                    "Did you forget to add something?"
                )
            )
            return

        # Raise error if raven is not configured.
        if not RAVEN_CONFIG:
            raise error

        # Send issue to sentry otherwise.
        from raven.contrib.django.raven_compat.models import client
        client.captureException()


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
