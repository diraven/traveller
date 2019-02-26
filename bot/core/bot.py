import re
from typing import List, Any

import discord
from discord.ext import commands

from settings import settings
from .context import Context
from .db import DB
from .message import Message
from .models import Guild, Alias


async def init_db() -> Any:
    return await DB.connect(
        settings.DB_USER,
        settings.DB_PASSWORD,
        settings.DB_NAME,
        settings.DB_HOST,
    )


async def get_prefix(bot: commands.Bot, message: discord.Message) -> List[str]:
    """Returns server prefix based on message."""
    # Get prefix from the database, create the guild if does not exist.
    async with DB.transaction():
        try:
            # Try to get prefix from the DB.
            db_guild = await Guild.get(message.guild.id)
            return commands.when_mentioned_or(db_guild.trigger)(bot, message)
        except AttributeError:
            # Save guild to the DB with the default prefix and use default
            # prefix.
            db_guild = Guild()
            db_guild.discord_id = message.guild.id
            db_guild.name = message.guild.name
            db_guild.trigger = settings.DISCORD_DEFAULT_PREFIX
            await db_guild.save()
            return commands.when_mentioned_or(db_guild.trigger)(bot, message)


class Bot(commands.Bot):
    def __init__(self, command_prefix=None, **options) -> None:
        if not command_prefix:
            command_prefix = get_prefix

        super().__init__(command_prefix=command_prefix, **options)

        self.loop.create_task(init_db())

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
                    '^{}{}'.format(ctx.prefix, alias.source),
                    '{}{}'.format(ctx.prefix, alias.target),
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
        from raven.contrib.django.raven_compat.models import client
        client.captureException()
