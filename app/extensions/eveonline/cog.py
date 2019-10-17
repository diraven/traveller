from discord.ext import commands, tasks
from discord import Color
from discord import Embed

from core.cogbase import CogBase
from core.context import Context
from core.emoji import EMOJI_UNICODE
from core.message import Message
from core.bot import Bot

import json

class Cog(CogBase):
    """A set of bot eve killmail commands."""
    @commands.group(
        invoke_without_command=True
    )
    async def killmail(
            self,
            ctx: Context
    ) -> None:
        """Show kill mail"""