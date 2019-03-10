"""
Game message module.
"""
from typing import Optional

import discord


class Message:
    """
    Game message class.
    """

    def __init__(
            self, *,
            text: str,
            title: str = None,
            icon: str = None,
            color: discord.Color = None
    ) -> None:
        self.text: str = text
        self.title: Optional[str] = title
        self.icon: Optional[str] = icon
        self.color: discord.Color = color

    @staticmethod
    def info(text: str, title: str = None) -> 'Message':
        """
        Returns prebuilt message object of info style.
        """
        return Message(
            text=text,
            title=title,
            icon=':information_source:',
            color=discord.Color.blue(),
        )

    @staticmethod
    def danger(text: str, title: str = None) -> 'Message':
        """
        Returns prebuilt message object of danger style.
        """
        if not title:
            title = "Oops..."
        return Message(
            text=text,
            title=title,
            icon=':no_entry:',
            color=discord.Color.red()
        )

    def as_text(self) -> str:
        """
        Returns message in a form of text piece directed to a single
        person if specified.
        """
        result = self.text

        if self.title:
            result = "**{}**\n{}".format(self.title, result)

        if self.icon:
            result = "{} {}".format(self.icon, result)

        return result

    def as_embed(self) -> discord.Embed:
        """
        Returns message in a form of embed directed to party as a whole.
        """
        title = ""
        if self.title:
            title = self.title
        if self.icon:
            title = "{} {}".format(self.icon, title)

        color = discord.Embed.Empty
        if self.color:
            color = self.color

        return discord.Embed(
            color=color,
            title=title,
            description=self.text,
        )
