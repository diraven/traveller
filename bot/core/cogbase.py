from discord.ext.commands import Cog

from core import Bot


class CogBase(Cog):
    _bot: Bot = None

    def __init__(self, bot: "Bot") -> None:
        self._bot = bot
