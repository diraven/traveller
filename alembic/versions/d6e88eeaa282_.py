"""empty message

Revision ID: d6e88eeaa282
Revises: 8896f4eed972
Create Date: 2024-05-22 21:21:58.690657

"""

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "d6e88eeaa282"
down_revision = "8896f4eed972"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column(
        "bans_sharing_bans", "created_by", existing_type=sa.BigInteger(), nullable=False
    )


def downgrade() -> None:
    op.alter_column(
        "bans_sharing_bans", "created_by", existing_type=sa.BigInteger(), nullable=True
    )
