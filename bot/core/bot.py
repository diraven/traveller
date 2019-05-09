"""Core bot module."""
import aiohttp
import discord
import re
import sentry_sdk
from discord.ext import commands
from typing import List

from settings import settings
from .context import Context
from .message import Message

if settings.SENTRY_DSN:
    sentry_sdk.init(settings.SENTRY_DSN)


async def get_prefix(bot: commands.Bot, message: discord.Message) -> List[str]:
    """Return server prefix based on message."""
    return commands.when_mentioned_or(
        settings.DISCORD_DEFAULT_PREFIX
    )(bot, message)


class Bot(commands.Bot):
    """Bot class."""

    def __init__(self, command_prefix=None, **options) -> None:
        """Make bot instance."""
        if not command_prefix:
            command_prefix = get_prefix

        super().__init__(command_prefix=command_prefix, **options)

    # async def close(self) -> None:
    #     """Close db connection."""
    #     await super().close()

    async def get_context(
            self,
            msg: discord.Message,
            *,
            cls=Context,
    ) -> Context:
        """Return command invocation context."""
        ctx: Context = await super().get_context(msg, cls=Context)

        # If command not found - try to find it using alias.
        if ctx.command is None and msg.guild:
            try:
                async with aiohttp.ClientSession().get(
                        f'http://app/api/aliases/?'
                        f'guild_discord_id={msg.guild.id}&'
                        f'source={ctx.invoked_with}',
                ) as response:
                    data = await response.json()
                    # Replace start of the message with the alias target.
                    msg.content = re.sub(
                        '^{}{}'.format(ctx.prefix, data[0]['source']),
                        '{}{}'.format(ctx.prefix, data[0]['target']),
                        msg.content,
                    )
                # Try to fetch context anew.
                ctx = await super().get_context(
                    msg,
                    cls=Context,
                )
            except IndexError:
                pass

        return ctx

    # noinspection PyBroadException
    async def on_command_error(self, ctx: Context, exception) -> None:
        """Global command errors handler."""
        if isinstance(exception, commands.errors.CommandInvokeError) and \
                isinstance(exception.original, discord.errors.Forbidden):
            await ctx.post(
                Message.danger(
                    "Unable to complete operation, "
                    f"missing necessary permissions: {exception.original}."
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

        if settings.SENTRY_DSN:
            # Send issue to sentry if configured.
            sentry_sdk.capture_exception(exception)
        else:
            # Raise error otherwise.
            return await super().on_command_error(ctx, exception)
