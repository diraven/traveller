"""empty message

Revision ID: a5766648953a
Revises:
Create Date: 2023-07-09 16:59:08.672441

"""

import sqlalchemy as sa

from alembic import op

revision = "a5766648953a"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "ban",
        sa.Column("id", sa.BigInteger(), nullable=False),
        sa.Column("reason", sa.String(length=500), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "guild",
        sa.Column("id", sa.BigInteger(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=True),
        sa.Column("log_channel_id", sa.BigInteger(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("guild")
    op.drop_table("ban")
