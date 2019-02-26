from typing import Optional, List

from core import Model, Field, DB


class PublicRole(Model):
    table_name = "publicroles_publicrole"

    discord_id = Field()
    guild_id = Field()

    @classmethod
    async def get(cls, discord_id: int) -> Optional['PublicRole']:
        return await cls._get_object(discord_id=discord_id)

    @classmethod
    async def get_all(cls, guild_discord_id: int) -> Optional[List['PublicRole']]:
        # noinspection SqlResolve
        result = await DB.get_connection().fetch(
            f'''SELECT pr.* FROM {cls.table_name} pr 
        LEFT JOIN mydiscord_guild g ON pr.guild_id = g.id
        WHERE g.discord_id = $1;
        ''',
            guild_discord_id,
        )

        if result:
            return [cls(**r) for r in result]
