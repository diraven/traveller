"""Welcome message database models."""
from core.models import db


class Welcome:
    """Data base for welcome module."""

    _collection = db.welcomes

    @classmethod
    async def get(cls, guild_id: int):
        """Retrieve guild from the database."""
        return await cls._collection.find_one({'guild_id': guild_id})

    @classmethod
    async def add(cls, guild_id: int, message: str):
        """Update role and delay in database."""
        return await cls._collection.update_one(
            {'guild_id': guild_id},
            {'$set': {'message': message}}, upsert=True,
        )

    @classmethod
    async def delete(cls, guild_id: int):
        """Delete guild from database."""
        return await cls._collection.delete_one(
            {'guild_id': guild_id},
        )
