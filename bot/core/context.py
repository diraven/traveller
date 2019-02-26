"""
Custom bot commands context.
"""
from typing import List, Dict, TYPE_CHECKING

import discord
from discord.ext import commands

if TYPE_CHECKING:
    from . import Bot, Message


class Context(commands.Context):
    def __init__(self, **attrs: Dict) -> None:
        self.message = None  # type: discord.Message
        self.bot = None  # type: Bot
        self.args = None  # type: List
        self.kwargs = None  # type: Dict
        self.prefix = None  # type: str
        self.command = None  # type: commands.Command
        # self.view = attrs.pop('view', None)
        # self.invoked_with = attrs.pop('invoked_with', None)
        # self.invoked_subcommand = attrs.pop('invoked_subcommand', None)
        # self.subcommand_passed = attrs.pop('subcommand_passed', None)
        # self.command_failed = attrs.pop('command_failed', False)
        # # noinspection PyProtectedMember
        # self._state = self.message._state

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
