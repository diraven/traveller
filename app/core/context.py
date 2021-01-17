"""Custom bot commands context."""
import typing

import discord
from discord.ext import commands

from core.emoji import EMOJI_UNICODE

if typing.TYPE_CHECKING:
    from core.bot import Bot


class Context(commands.Context):
    """Bot command context."""

    def __init__(self, **attrs: typing.Dict) -> None:
        """Make new context."""
        self.message: discord.message
        self.bot: "Bot"
        self.args: typing.List
        self.kwargs: typing.Dict
        self.prefix: str
        self.command: commands.Command

        super().__init__(**attrs)

    async def post_info(self, text: str):
        """Send info message."""
        return await self.send(
            embed=discord.Embed(
                description=text,
                title=":information_source:",
                color=discord.Color.blue(),
            )
        )

    async def post_warning(self, text: str):
        """Send warning message."""
        return await self.send(
            embed=discord.Embed(
                description=text,
                title=":warning:",
                color=discord.Color.orange(),
            )
        )

    async def post_error(self, text: str):
        """Send error message."""
        return await self.send(
            embed=discord.Embed(
                description=text,
                title=":no_entry:",
                color=discord.Color.red(),
            )
        )

    async def react_ok(self) -> discord.Reaction:
        """Add ok hand reaction to the message."""
        return await self.message.add_reaction(EMOJI_UNICODE[":OK_hand:"])
