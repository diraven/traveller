"""Base bot models module."""
from typing import Optional

from core.db import Field, Model, DB


class Character(Model):
    """Command alias."""

    table_name = "theburningclaw_character"

    name = Field()

    @classmethod
    async def get_or_create(
            cls, *,
            user_id: int,
            character_name: str,
    ) -> Optional['Character']:
        """Retrieve character by discord user id."""
        # noinspection SqlResolve
        await DB.get_connection().execute(
            f'''
INSERT INTO {cls.table_name} (user_id, name)
VALUES ($1, $2) ON CONFLICT DO NOTHING;
            ''',
            user_id,
            character_name,
        )
        return await cls._get_object(user_id=user_id)
