from typing import Any

from ..db import DB
from ..field import Field
from ..model import Model


class Alias(Model):
    table_name = "mydiscord_alias"

    source = Field()
    target = Field()
    guild_id = Field()

    @classmethod
    async def get(cls, guild_discord_id: int, source: str) -> Any:
        result = await DB.get_connection().fetchrow(
            '''
            SELECT a.* FROM mydiscord_alias a 
            LEFT JOIN mydiscord_guild g ON a.guild_id = g.id
            WHERE g.discord_id = $1 AND a.source = $2;
            ''',
            guild_discord_id,
            source,
        )

        if result:
            return cls(**result)
