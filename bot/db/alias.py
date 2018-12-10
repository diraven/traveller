from typing import Any

from .db import DB


class Alias:
    @staticmethod
    async def get(guild_discord_id: int, source: str) -> Any:
        return await DB.get_connection().fetchrow(
            '''
            SELECT * FROM mydiscord_alias a 
            LEFT JOIN mydiscord_guild g ON a.guild_id = g.id
            WHERE g.discord_id = $1 AND a.source = $2;
            ''',
            guild_discord_id,
            source,
        )
