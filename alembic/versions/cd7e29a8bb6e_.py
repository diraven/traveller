"""empty message

Revision ID: cd7e29a8bb6e
Revises: 1e25f28c9227
Create Date: 2024-05-22 21:07:55.019257

"""

import sqlalchemy as sa

from alembic import op

revision = "cd7e29a8bb6e"
down_revision = "1e25f28c9227"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "bans_sharing_bans", sa.Column("created_by", sa.BigInteger(), nullable=True)
    )


def downgrade() -> None:
    op.drop_column("bans_sharing_bans", "created_by")
