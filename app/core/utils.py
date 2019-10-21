"""Bot generic utilities module."""
import enum
import re
import typing

from discord.ext import commands
from discord.ext.commands import CheckFailure

from core.emoji import EMOJI_ALIAS_UNICODE

DEFAULT_TIMEOUT = 10
MAX_PAGE_LEN = 1000


# noinspection PyUnresolvedReferences,PyTypeChecker
@enum.unique
class Button(enum.Enum):
    """Control buttons."""

    ARROW_LEFT = EMOJI_ALIAS_UNICODE[':arrow_backward:']
    ARROW_RIGHT = EMOJI_ALIAS_UNICODE[':arrow_forward:']
    OPTION_1 = '\U0001F1E6'
    OPTION_2 = '\U0001F1E7'
    OPTION_3 = '\U0001F1E8'
    OPTION_4 = '\U0001F1E9'
    OPTION_5 = '\U0001F1EA'

    @classmethod
    def values(cls) -> typing.List[str]:
        """Button values."""
        return [b.value for b in cls]


special_symbols = re.compile(r'([_*~`])')


def escape(text: str) -> str:
    """Escape special symbols for discord."""
    return re.sub(special_symbols, r'\\\1', text)


def is_owner_or_admin() -> typing.Callable:
    """Check if user is either owner or admin."""
    async def predicate(ctx):
        if await ctx.bot.is_owner(ctx.author):
            return True
        if ctx.author.guild_permissions.administrator:
            return True
        raise CheckFailure('Neither owner nor admin.')

    return commands.check(predicate)
