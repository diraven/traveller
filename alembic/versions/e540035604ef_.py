"""empty message

Revision ID: e540035604ef
Revises: a5766648953a
Create Date: 2023-07-11 14:38:52.585476

"""

from alembic import op

revision = "e540035604ef"
down_revision = "a5766648953a"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column(
        "guild", "log_channel_id", new_column_name="bans_sharing_channel_id"
    )


def downgrade() -> None:
    op.alter_column(
        "guild", "bans_sharing_channel_id", new_column_name="log_channel_id"
    )
