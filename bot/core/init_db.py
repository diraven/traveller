from typing import Any

from bot.db import DB
from bot.settings import settings


async def init_db() -> Any:
    return await DB.connect(
        settings.DB_USER,
        settings.DB_PASSWORD,
        settings.DB_NAME,
        'localhost',
    )
