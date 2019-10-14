"""Bot database models."""
import typing

import motor.motor_asyncio

db = motor.motor_asyncio.AsyncIOMotorClient('mongo').crabot


class Server:
    """Database guild(server) model."""

    @staticmethod
    async def get_or_create(id_: typing.Any):
        """Retrieve (or create and retrieve) guild from the database."""
        created = False
        server = await db.servers.find_one({'id': id_})
        if not server:
            server = {
                'id': id_,
                'status': False,
                'role': None,
                'delay': 10.0}
            await db.servers.insert_one(server)
            created = True
        return server, created

    @staticmethod
    async def update_role(id_: typing.Any, role_id: typing.Any):
        if await db.servers.update_one(
            {'id': id_},
            {'$set': {'role': role_id}},
        ):
            return True
        else:
            return False

    @staticmethod
    async def update_status(id_: typing.Any, status: typing.Any):
        if await db.servers.update_one(
            {'id': id_},
            {'$set': {'status': status}},
        ):
            return True
        else:
            return False

    @staticmethod
    async def set_delay(id_: typing.Any, delay: typing.Any):
        if await db.servers.update_one(
            {'id': id_},
            {'$set': {'delay': delay}}
        ):
            return True
        else:
            return False
