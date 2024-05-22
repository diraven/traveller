"""empty message

Revision ID: ed3b272e0ccf
Revises: 203358c88297
Create Date: 2023-08-20 18:05:02.266325

"""

from alembic import op

revision = "ed3b272e0ccf"
down_revision = "203358c88297"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column(
        "guild",
        "id",
        new_column_name="id_",
    )
    op.alter_column(
        "ban",
        "id",
        new_column_name="id_",
    )


def downgrade() -> None:
    op.alter_column(
        "guild",
        "id_",
        new_column_name="id",
    )
    op.alter_column(
        "ban",
        "id_",
        new_column_name="id",
    )
