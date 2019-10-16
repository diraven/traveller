"""Bot database models."""
from core.db import db


class Alias:
    """Database guild model."""

    _collection = db.aliases

    @classmethod
    async def get(cls, *, guild_id: int, src: str):
        """Find alias."""
        return await cls._collection.find_one({
            'guild_id': guild_id,
            'src': src,
        })

    @classmethod
    async def get_by_guild(cls, *, guild_id: int):
        """Get all guild aliases."""
        return await cls._collection.find({
            'guild_id': guild_id,
        }).to_list(100)

    @classmethod
    async def set(cls, *, guild_id: int, src: str, dst: str):
        """Add command alias."""
        return await cls._collection.update_one({
            'guild_id': guild_id,
            'src': src,
        }, {
            '$set': {'dst': dst},
        }, upsert=True)

    @classmethod
    async def delete(cls, *, guild_id: int, src: str):
        """Delete command alias."""
        return await cls._collection.delete_many(
            {
                'guild_id': guild_id,
                'src': src,
            },
        )
