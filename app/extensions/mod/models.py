"""Bot database models."""
import enum
import time

from core.database import db


@enum.unique
class LogRecordType(enum.Enum):
    """Types of the log records."""

    NOTE = 'note'
    WARNING = 'warning'
    KICK = 'kick'
    BAN = 'ban'


class UserLog:
    """LogRecord db model."""

    _collection = db.user_log

    @classmethod
    async def get(cls, *, guild_id: int, user_id: int):
        """Get user's log records."""
        return cls._collection.find({
            'guild_id': guild_id,
            'user_id': user_id,
        }).sort('created_at', -1)

    @classmethod
    async def add_record(
            cls, *,
            guild_id: int,
            user_id: int,
            author_user_id: int,
            type_: LogRecordType,
            text: str,
    ):
        """Add log record."""
        return await cls._collection.insert_one({
            'created_at': time.time(),
            'guild_id': guild_id,
            'user_id': user_id,
            'author_user_id': author_user_id,
            'type': type_.value,
            'text': text,
        })
