"""Bot database interactions module."""
import typing
from typing import Any

import asyncpg


class DB:
    """Bot's DB access implementation."""

    _connection: asyncpg.connection.Connection = None

    @staticmethod
    async def connect(
            user: typing.Optional[str],
            password: typing.Optional[str],
            database: typing.Optional[str],
            host: typing.Optional[str],
    ) -> None:
        """Connect to the database."""
        DB._connection = await asyncpg.connect(
            user=user,
            password=password,
            database=database,
            host=host
        )

    @staticmethod
    async def disconnect() -> None:
        """Disconnect from database."""
        await DB._connection.close()

    @staticmethod
    def get_connection() -> asyncpg.connection.Connection:
        """Get database connection."""
        if DB._connection is None:
            raise Exception('Not connected to the database.')
        return DB._connection

    @staticmethod
    def transaction(*, isolation='read_committed', readonly=False,
                    deferrable=False) -> Any:
        """Make and return new transaction."""
        return DB._connection.transaction(isolation=isolation,
                                          readonly=readonly,
                                          deferrable=deferrable)


class Field:
    """Generic database field."""

    pass


class Model:
    """Generic database model."""

    table_name: str = ''

    id = Field()

    def __init__(self, **kwargs) -> None:
        """Create new object of the given model."""
        # Gather fields list.
        self._field_names = [
            field for field in dir(self) if
            isinstance(getattr(self, field), Field)
        ]

        # For each field:
        for field in self._field_names:
            # If field value provided:
            if field in kwargs:
                # Set instance attribute to the field value provided.
                setattr(self, field, kwargs[field])
            else:
                # Also set all the rest of the instance attributes to None to
                # make sure to not accidentally access class-level attributes.
                setattr(self, field, None)

    async def save(self) -> None:
        """Save object into the database."""
        # Copy field names list.
        field_names = self._field_names[:]

        # If ID is not provided in the model:
        if not self.id:
            # Do not build it into the query.
            field_names.remove('id')

        # Build data placeholders to be inserted.
        placeholders = ', '.join(
            ['$' + str(i) for i in range(1, len(field_names) + 1)]
        )

        # Build values to be inserted.
        values = [
            getattr(self, field_name) for field_name in field_names
        ]

        if self.id:  # UPDATE
            set_statement = [
                f'{couple[0]} = {couple[1]}'
                for couple in zip(field_names, placeholders)
            ]
            # noinspection SqlResolve
            await DB.get_connection().execute(
                f'''
                UPDATE {self.table_name}
                SET {set_statement}
                WHERE id={self.id};
                ''',
                *values,
            )
        else:  # INSERT
            # Build fields to be inserted.
            fields_statement = ", ".join(field_names)

            await DB.get_connection().execute(
                f'''INSERT INTO {self.table_name}({fields_statement})
                VALUES ({placeholders});
                ''',
                *values,
            )

    async def delete(self) -> Any:
        """Remove the alias."""
        # noinspection SqlResolve
        return await DB.get_connection().execute(
            f'DELETE FROM {self.table_name} WHERE id=$1',
            self.id,
        )

    @classmethod
    def _build_select_query(cls, **kwargs) -> str:
        # Convert kwargs into the simple where clause.
        where_clause = " AND ".join(
            f"{name} = ${idx + 1}" for idx, name in enumerate(kwargs.keys())
        )

        # Build the query.
        return f'''SELECT * FROM {cls.table_name} WHERE {where_clause};'''

    @classmethod
    async def _get_object(cls, **kwargs) -> Any:

        # Execute the query.
        result = await DB.get_connection().fetchrow(
            cls._build_select_query(**kwargs), *kwargs.values())

        # If result available - return it in the form of class instance.
        if result:
            return cls(**result)

    @classmethod
    async def _get_objects(cls, **kwargs) -> Any:
        # Execute the query.
        result = await DB.get_connection().fetch(
            cls._build_select_query(**kwargs), *kwargs.values())

        # If result available - return it in the form of class instance.
        return [cls(**r) for r in result]
