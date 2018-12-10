from typing import List

import discord
from discord.ext import commands

from bot.db import DB, Guild
from bot.settings import settings


async def get_prefix(bot: commands.Bot, message: discord.Message) -> List[str]:
    """Returns server prefix based on message."""
    # Get prefix from the database, create the guild if does not exist.
    async with DB.transaction():
        try:
            # Try to get prefix from the DB.
            db_guild = await Guild.get(message.guild.id)
            return commands.when_mentioned_or(db_guild.trigger)(bot, message)
        except AttributeError:
            # Save guild to the DB with the default prefix and use default
            # prefix.
            db_guild = Guild()
            db_guild.discord_id = message.guild.id
            db_guild.name = message.guild.name
            db_guild.trigger = settings.DISCORD_DEFAULT_PREFIX
            await db_guild.save()
            return commands.when_mentioned_or(db_guild.trigger)(bot, message)
