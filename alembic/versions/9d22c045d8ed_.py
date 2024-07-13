"""empty message

Revision ID: 9d22c045d8ed
Revises: ed3b272e0ccf
Create Date: 2024-05-22 20:57:08.957579

"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "9d22c045d8ed"
down_revision = "ed3b272e0ccf"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.rename_table("ban", "bans")
    op.rename_table("guild", "guilds")


def downgrade() -> None:
    op.rename_table("bans", "ban")
    op.rename_table("guilds", "guild")
