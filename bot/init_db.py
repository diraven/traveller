from typing import Any

import settings_local

from bot import DB


async def init_db() -> Any:
    return await DB.connect(
        settings_local.DATABASES['default']['USER'],
        settings_local.DATABASES['default']['PASSWORD'],
        settings_local.DATABASES['default']['NAME'],
        'localhost',
    )
