"""Core bot module."""
import re
import typing as t

import discord
import sentry_sdk
from discord.ext import commands
from settings import settings

from core import paginators, utils
from core.models import Alias
from core.context import Context

if settings.SENTRY_DSN:
    sentry_sdk.init(settings.SENTRY_DSN)


async def get_prefix(bot: commands.Bot, message: discord.Message) -> t.List[str]:
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

    async def get_context(
        self,
        message: discord.Message,
        *,
        cls=Context,
    ) -> Context:
        """Return command invocation context."""
        ctx: Context = await super().get_context(message, cls=cls)

        if ctx.command is None and message.guild:
            alias = await Alias.get(
                guild_id=message.guild.id,
                src=ctx.invoked_with,
            )
            if alias:
                message.content = re.sub(
                    "^{}{}".format(ctx.prefix, alias["src"]),
                    "{}{}".format(ctx.prefix, alias["dst"]),
                    message.content,
                )
                ctx = await super().get_context(
                    message,
                    cls=Context,
                )

        return ctx

    # noinspection PyBroadException
    async def on_command_error(self, context: Context, exception) -> None:
        """Global command errors handler."""
        if isinstance(exception, commands.errors.CommandInvokeError) and isinstance(
            exception.original, discord.errors.Forbidden
        ):
            await context.post_error(
                f"{exception.original.response.url}.\n"
                f"{exception.original.response.method}: \n"
                f"{exception.original.response.reason}",
            )
            return

        # Ignore other checks failures.
        if isinstance(
            exception,
            (
                commands.CheckFailure,
                commands.CommandNotFound,
            ),
        ):
            return

        # Pass some exceptions to the user directly.
        if isinstance(exception, (commands.errors.UserInputError,)):
            await context.post_error(str(exception))
            return

        if settings.SENTRY_DSN:
            # Send issue to sentry if configured.
            sentry_sdk.capture_exception(exception)
        else:
            # Raise error otherwise.
            return await super().on_command_error(context, exception)


class CogBase(commands.Cog):
    """Cog base."""

    def __init__(self, bot: "Bot") -> None:
        """Create cog."""
        self._bot = bot


class Cog(CogBase):
    """Core cog."""

    @commands.command()
    async def about(
        self,
        ctx: Context,
    ) -> None:
        """Show information about bot developer."""
        await ctx.post_info(
            "**Developer:** DiRaven#0519 \n"
            "**Sources:** https://github.com/diraven/crabot \n",
        )

    @commands.command()
    async def ping(
        self,
        ctx: Context,
    ) -> None:
        """Show information about bot developer."""
        await ctx.post_info("Pong!")

    @commands.group(invoke_without_command=True)
    @utils.is_owner_or_admin()
    async def aliases(
        self,
        ctx: Context,
    ) -> None:
        """Show configured aliases."""
        docs = await Alias.get_by_guild(guild_id=ctx.guild.id)
        await paginators.post_from_motor(
            ctx=ctx,
            data=docs,
            title="command aliases",
            formatter=lambda x: f'`{x["src"]}` -> `{x["dst"]}`',
        )

    @aliases.command(name="set")
    @utils.is_owner_or_admin()
    async def aliases_set(
        self,
        ctx: Context,
        src: str,
        dst: str,
    ) -> None:
        """Set alias."""
        await Alias.upsert(
            guild_id=ctx.guild.id,
            src=src,
            dst=dst,
        )
        await ctx.react_ok()

    @aliases.command(name="del")
    @utils.is_owner_or_admin()
    async def aliases_del(
        self,
        ctx: Context,
        query: str,
    ) -> None:
        """Delete alias."""
        count = await Alias.delete(
            guild_id=ctx.guild.id,
            src=query,
        )
        if count:
            await ctx.react_ok()
        else:
            await ctx.post_warning("No such alias was found.")
