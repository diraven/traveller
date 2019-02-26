"""
Game message module.
"""
from typing import Optional

import discord


class Message:
    """
    Game message class.
    """
    _title = ""  # type: Optional[str]
    _text = ""  # type: str
    _icon = ""  # type: Optional[str]
    _color = ""  # type: discord.Color

    def __init__(self, *, text: str, title: str = None, icon: str = None, color: discord.Color = None) -> None:
        self._title = title
        self._text = text
        self._icon = icon
        self._color = color

    def set_title(self, title: str) -> None:
        """
        Sets title on the already existent message.
        """
        self._title = title

    def set_text(self, text: str) -> None:
        """
        Sets text on the already existent message.
        """
        self._text = text

    def set_icon(self, icon: str) -> None:
        """
        Sets icon on the already existent message.
        """
        self._icon = icon

    def set_color(self, color: str) -> None:
        """
        Sets color on the already existent message.
        """
        self._color = color

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
        result = self._text

        if self._title:
            result = "**{}**\n{}".format(self._title, result)

        if self._icon:
            result = "{} {}".format(self._icon, result)

        return result

    def as_embed(self) -> discord.Embed:
        """
        Returns message in a form of embed directed to party as a whole.
        """
        title = ""
        if self._title:
            title = self._title
        if self._icon:
            title = "{} {}".format(self._icon, title)

        color = discord.Embed.Empty
        if self._color:
            color = self._color

        return discord.Embed(
            color=color,
            title=title,
            description=self._text,
        )
