from typing import List

import discord
import settings_local
from discord.ext import commands

from bot import DB
from bot.db.guild import Guild


async def get_prefix(bot: commands.Bot, message: discord.Message) -> List[str]:
    """Returns server prefix based on message."""
    # Set default prefix.
    prefix = settings_local.DISCORD_DEFAULT_PREFIX

    # Get prefix from the database, create the guild if does not exist.
    async with DB.transaction():
        # Get guild we are interested in.
        db_guild = await Guild.get(message.guild.id)

        # If guild does not exist in the DB - put it there.
        if not db_guild and message.guild:
            await Guild.put(
                message.guild.id,
                message.guild.name,
                prefix,
            )

    return commands.when_mentioned_or(prefix)(bot, message)
