from typing import Any

from .db import DB
from .field import Field


class Model:
    table_name = None

    id = Field()

    def __init__(self, **kwargs) -> None:
        # Gather fields list.
        self._field_names = [field for field in dir(self) if
                             isinstance(getattr(self, field), Field)]

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
        # Copy field names list.
        field_names = self._field_names[:]

        # If ID is not provided in the model:
        if not self.id:
            # Do not build it into the query.
            field_names.remove('id')

        # Build fields to be inserted.
        fields = ", ".join(field_names)

        # Build data placeholders to be inserted.
        placeholders = ', '.join(
            ['$' + str(i) for i in range(1, len(field_names) + 1)]
        )

        # Build values to be inserted.
        values = [
            getattr(self, field_name) for field_name in field_names
        ]

        # Perform the insert itself.
        await DB.get_connection().execute(
            f'''INSERT INTO {self.table_name}({fields}) 
            VALUES ({placeholders});
            ''',
            *values,
        )

    @classmethod
    async def get_object(cls, **kwargs) -> Any:
        # Convert kwargs into the simple where clause.
        where_clause = " AND ".join(
            f"{name} = ${idx + 1}" for idx, name in enumerate(kwargs.keys())
        )

        # Build the query.
        query = f'''SELECT * FROM {cls.table_name} WHERE {where_clause};'''

        # Execute the query.
        result = await DB.get_connection().fetchrow(query, *kwargs.values())

        # If result available - return it in the form of class instance.
        if result:
            return cls(**result)
