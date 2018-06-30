"""
Custom bot commands context.
"""
from typing import Optional

import discord
from discord.ext.commands import Context as DiscordPyContext

from mydiscord.message import Message


class Context(DiscordPyContext):
    async def react(
            self,
            reaction: str,
            msg: Optional[discord.Message] = None,
    ) -> discord.Reaction:
        """
        Adds reaction to the message.
        """
        if not msg:
            msg = self.message
        return await msg.add_reaction(reaction)

    async def acknowledge(
            self,
            msg: Optional[discord.Message] = None
    ) -> discord.Reaction:
        """
        Marks message as acknowledged by bot.
        """
        return await self.react("🦀")

    async def success(
            self,
            msg: Optional[discord.Message] = None
    ) -> discord.Reaction:
        """
        Marks message as confirmed by bot.
        """
        return await self.react("✅")

    async def post(self, message: Message,
                   with_mention: bool = True) -> discord.Message:
        """
        Posts response to party, or to player if specified.
        """

        if with_mention:
            return await self.send(
                "{}\n{}".format(
                    self.message.author.mention,
                    message.as_text()),
            )

        return await self.send(embed=message.as_embed())
