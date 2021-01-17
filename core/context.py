"""Custom bot commands context."""
import discord
from discord.ext import commands

from core.emoji import EMOJI_UNICODE


class Context(commands.Context):
    """Bot command context."""

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
