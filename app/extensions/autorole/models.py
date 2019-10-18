"""Bot database models."""
from core.models import db


class Autorole:
    """Database guild(server) model."""

    _collection = db.autoroles

    @classmethod
    async def get(cls, guild_id: int):
        """Retrieve (or create and retrieve) guild from the database."""
        return await cls._collection.find_one({'id': guild_id})

    @classmethod
    async def update_role(cls, guild_id: int, role_id: int):
        """Update role in database."""
        return await cls._collection.update_one(
            {'id': guild_id},
            {'$set': {'role': role_id}}, upsert=True,
        )

    @classmethod
    async def set_delay(cls, guild_id: int, delay: float):
        """Update delay in database."""
        return await cls._collection.update_one(
            {'id': guild_id},
            {'$set': {'delay': delay}}, upsert=True,
        )

    @classmethod
    async def guild_delete(cls, guild_id: int):
        """Delete guild from database."""
        return await cls._collection.delete_one(
            {'id': guild_id},
        )
