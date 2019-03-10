"""
Custom bot commands context.
"""
import typing
from typing import List, Dict, TYPE_CHECKING

import discord
from discord.ext import commands

if TYPE_CHECKING:
    from . import Bot, Message


class Context(commands.Context):
    def __init__(self, **attrs: Dict) -> None:
        self.message: discord.message = None
        self.bot: Bot = None
        self.args: typing.List = None
        self.kwargs: typing.Dict = None
        self.prefix: str = None
        self.command: commands.Command = None

        super().__init__(**attrs)

    async def post(
            self,
            message: 'Message',
            with_mention: bool = False
    ) -> discord.Message:
        """
        Send response as embed, or as text with mention if requested.
        """

        if with_mention:
            return await self.send(
                "{}\n{}".format(
                    self.message.author.mention,
                    message.as_text()),
            )

        return await self.send(embed=message.as_embed())
