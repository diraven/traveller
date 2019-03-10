"""Custom bot commands context."""
import typing

import discord
from discord.ext import commands

if typing.TYPE_CHECKING:
    from . import Bot, Message


class Context(commands.Context):
    """Bot command context."""

    def __init__(self, **attrs: typing.Dict) -> None:
        """Make new context."""
        self.message: discord.message
        self.bot: Bot
        self.args: typing.List
        self.kwargs: typing.Dict
        self.prefix: str
        self.command: commands.Command

        super().__init__(**attrs)

    async def post(
            self,
            message: 'Message',
            with_mention: bool = False
    ) -> discord.Message:
        """Send response as embed, or as text with mention if requested."""
        if with_mention:
            return await self.send(
                "{}\n{}".format(
                    self.message.author.mention,
                    message.as_text()),
            )

        return await self.send(embed=message.as_embed())
