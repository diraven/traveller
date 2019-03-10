"""Basic cog implementation."""
from discord.ext.commands import Cog

from core import Bot


class CogBase(Cog):
    """Cog base."""

    def __init__(self, bot: "Bot") -> None:
        """Create cog."""
        self._bot = bot
