from typing import Optional

from ..field import Field
from ..model import Model


class Guild(Model):
    table_name = "mydiscord_guild"

    discord_id = Field()
    name = Field()
    trigger = Field()

    @classmethod
    async def get(cls, discord_id: str) -> Optional['Guild']:
        return await cls.get_object(discord_id=discord_id)
