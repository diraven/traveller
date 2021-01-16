"""Basic cog implementation."""
from typing import TYPE_CHECKING

from discord.ext.commands import Cog

if TYPE_CHECKING:
    from core.bot import Bot


class CogBase(Cog):
    """Cog base."""

    def __init__(self, bot: "Bot") -> None:
        """Create cog."""
        self._bot = bot
