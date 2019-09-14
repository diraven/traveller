import typing

import motor.motor_asyncio

db = motor.motor_asyncio.AsyncIOMotorClient('mongo').crabot


class Guild:
    @staticmethod
    async def get_or_create(id_: typing.Any):
        created = False
        guild = await db.guilds.find_one({"id": id_})
        if not guild:
            guild = {'id': id_, 'aliases': []}
            await db.guilds.insert_one(guild)
            created = True
        return guild, created

    @staticmethod
    async def add_alias(*, guild_id: str, src: str, dst: str):
        r = await db.guilds.update_one(
            {
                'id': guild_id,
                'aliases.src': {'$ne': src},
            },
            {'$push': {'aliases': {
                'src': src,
                'dst': dst,
            }}},
        )
        return r.modified_count

    @staticmethod
    async def del_alias(*, guild_id: str, src: str):
        r = await db.guilds.update_one(
            {
                'id': guild_id,
                'aliases.src': src,
            },
            {'$pull': {'aliases': {
                'src': src,
            }}},
        )
        return r.modified_count
