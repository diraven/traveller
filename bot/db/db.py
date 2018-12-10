from typing import Any

import asyncpg


class DB:
    _connection = None  # type: asyncpg.connection.Connection

    @staticmethod
    async def connect(
            user: str,
            password: str,
            database: str,
            host: str
    ) -> None:
        DB._connection = await asyncpg.connect(
            user=user,
            password=password,
            database=database,
            host=host
        )

    @staticmethod
    async def disconnect() -> None:
        await DB._connection.close()

    @staticmethod
    def get_connection() -> asyncpg.connection.Connection:
        if DB._connection is None:
            raise Exception('Not connected to the database.')
        return DB._connection

    @staticmethod
    def transaction(*, isolation='read_committed', readonly=False,
                    deferrable=False) -> Any:
        return DB._connection.transaction(isolation=isolation,
                                          readonly=readonly,
                                          deferrable=deferrable)
