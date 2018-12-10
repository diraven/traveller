from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from bot import Bot


class CogBase:
    _bot = None  # type: Bot

    def __init__(self, bot: "Bot") -> None:
        self._bot = bot
