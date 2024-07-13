"""empty message

Revision ID: 04ca088b8f21
Revises: e540035604ef
Create Date: 2023-07-11 15:20:48.710851

"""

import sqlalchemy as sa

from alembic import op

revision = "04ca088b8f21"
down_revision = "e540035604ef"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "guild", sa.Column("verification_role_id", sa.BigInteger(), nullable=True)
    )


def downgrade() -> None:
    op.drop_column("guild", "verification_role_id")
