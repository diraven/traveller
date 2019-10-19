"""Core bot module."""
import re
from typing import List

import discord
import sentry_sdk
from discord.ext import commands

from core.cog import Cog
from core.models import Alias
from settings import settings
from .context import Context
from .message import Message

if settings.SENTRY_DSN:
    sentry_sdk.init(settings.SENTRY_DSN)


async def get_prefix(bot: commands.Bot, message: discord.Message) -> List[str]:
    """Return server prefix based on message."""
    return commands.when_mentioned_or(
        settings.DISCORD_DEFAULT_PREFIX,
    )(bot, message)


class Bot(commands.Bot):
    """Bot class."""

    def __init__(self, command_prefix=None, **options) -> None:
        """Initialize bot."""
        if not command_prefix:
            command_prefix = get_prefix

        super().__init__(command_prefix=command_prefix, **options)
        self.add_cog(Cog(self))  # load core cog

    async def on_connect(self):
        """Perform operations on successful connect."""
        await self.migrate()

    @staticmethod
    async def migrate():
        """Perform DB migrations."""
        pass

    async def get_context(
            self,
            msg: discord.Message,
            *,
            cls=Context,
    ) -> Context:
        """Return command invocation context."""
        ctx: Context = await super().get_context(msg, cls=Context)

        if ctx.command is None and msg.guild:
            alias = await Alias.get(
                guild_id=msg.guild.id,
                src=ctx.invoked_with,
            )
            if alias:
                msg.content = re.sub(
                    '^{}{}'.format(ctx.prefix, alias['src']),
                    '{}{}'.format(ctx.prefix, alias['dst']),
                    msg.content,
                )
                ctx = await super().get_context(
                    msg,
                    cls=Context,
                )

        return ctx

    # noinspection PyBroadException
    async def on_command_error(self, ctx: Context, exception) -> None:
        """Global command errors handler."""
        if isinstance(exception, commands.errors.CommandInvokeError) and \
                isinstance(exception.original, discord.errors.Forbidden):
            await ctx.post(
                Message.danger(
                    f' {exception.original.response.url}.',
                    title=f'Oops... Unable to '
                          f'{exception.original.response.method}: '
                          f'{exception.original.response.reason}',
                ),
            )
            return

        # Ignore other checks failures.
        if isinstance(
                exception, commands.CheckFailure,
        ) or isinstance(
            exception, commands.CommandNotFound,
        ):
            return

        # Pass some exceptions to the user directly.
        if isinstance(exception, (
                commands.errors.UserInputError,
        )):
            await ctx.post(Message.danger(str(exception)))
            return

        if settings.SENTRY_DSN:
            # Send issue to sentry if configured.
            sentry_sdk.capture_exception(exception)
        else:
            # Raise error otherwise.
            return await super().on_command_error(ctx, exception)
