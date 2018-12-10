import re

import discord
from discord.ext import commands

from bot.db import DB, Alias
from bot.settings import settings
from .context import Context
from .message import Message


class Bot(commands.Bot):
    async def close(self) -> None:
        await DB.disconnect()
        await super().close()

    async def get_context(self, msg: discord.Message, *,
                          cls=Context) -> Context:
        """
        Returns command invocation context.
        """
        ctx = await super().get_context(msg, cls=Context)  # type: Context

        # If command not found - try to find it using alias.
        if ctx.command is None and msg.guild:
            alias = await Alias.get(msg.guild.id, ctx.invoked_with)
            if alias:
                # Replace start of the message with the alias target.
                msg.content = re.sub(
                    '^{}{}'.format(self.command_prefix, alias['source']),
                    '{}{}'.format(self.command_prefix, alias['target']),
                    msg.content,
                )
            # Try to fetch context anew.
            ctx = await super().get_context(
                msg,
                cls=Context,
            )

        return ctx

    # noinspection PyBroadException
    async def on_command_error(self, ctx: Context, exception) -> None:
        """
        Global command errors handler.
        """
        if isinstance(exception, commands.errors.CommandInvokeError) and \
                isinstance(exception.original, discord.errors.Forbidden):
            await ctx.post(
                Message.danger(
                    "Unable to complete operation, "
                    "missing necessary permissions."
                )
            )
            return

        # Ignore other checks failures.
        if isinstance(
                exception, commands.CheckFailure
        ) or isinstance(
            exception, commands.CommandNotFound
        ):
            return

        # Process missing command arguments error by responding to the user.
        if isinstance(exception, commands.MissingRequiredArgument):
            await ctx.post(
                Message.danger(
                    "Incorrect command usage, missing argument. "
                    "Did you forget to add something?"
                )
            )
            return

        # Raise error if raven is not configured.
        if not settings.RAVEN_CONFIG:
            return await super().on_command_error(ctx, exception)

        # Send issue to sentry otherwise.
        # TODO Implement proper raven sending without django.
        from raven.contrib.django.raven_compat.models import client
        client.captureException()
