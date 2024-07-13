"""empty message

Revision ID: 1e25f28c9227
Revises: 9d22c045d8ed
Create Date: 2024-05-22 21:04:16.105369

"""

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "1e25f28c9227"
down_revision = "9d22c045d8ed"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.rename_table("bans", "bans_sharing_bans")
    op.create_table(
        "bans_sharing_trusted_moderators",
        sa.Column("id_", sa.BigInteger(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_by", sa.BigInteger(), nullable=False),
        sa.Column("guild_id", sa.BigInteger(), nullable=False),
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.PrimaryKeyConstraint("id_"),
    )


def downgrade() -> None:
    op.rename_table("bans_sharing_bans", "bans")
    op.drop_table("bans_sharing_bans")
