from typing import Any

from bot.db import DB


class Guild:
    @staticmethod
    async def get(discord_id: str) -> Any:
        return await DB.get_connection().fetch(
            '''SELECT * FROM mydiscord_guild WHERE discord_id = $1;''',
            discord_id,
        )

    @staticmethod
    async def put(discord_id: str, name: str, trigger: str) -> Any:
        return await DB.get_connection().execute(
            '''
            INSERT INTO mydiscord_guild(discord_id, name, trigger) 
            VALUES ($1, $2, $3);
            ''',
            discord_id,
            name,
            trigger,
        )
