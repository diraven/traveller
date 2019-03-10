"""Base bot models module."""
import typing
from typing import Optional

from core.db import Model, Field, DB


class Alias(Model):
    """Command alias."""

    table_name = "mydiscord_alias"

    source = Field()
    target = Field()
    guild_id = Field()

    @classmethod
    async def get(
            cls,
            guild_discord_id: int,
            source: str,
    ) -> Optional['Alias']:
        """Retrieve command alias."""
        # noinspection SqlResolve
        result = await DB.get_connection().fetchrow(
            f'''SELECT a.* FROM {cls.table_name} a
            LEFT JOIN mydiscord_guild g ON a.guild_id = g.id
            WHERE g.discord_id = $1 AND a.source = $2;
            ''',
            guild_discord_id,
            source,
        )

        return cls(**result) or None


class Guild(Model):
    """Database representation of the guild."""

    table_name = "mydiscord_guild"

    discord_id = Field()
    name = Field()
    trigger: typing.Union[Field, typing.Optional[str]] = Field()

    @classmethod
    async def get(cls, discord_id: int) -> 'Guild':
        """Get database representation of the guild."""
        return await cls._get_object(discord_id=discord_id)
