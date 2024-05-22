"""empty message

Revision ID: 203358c88297
Revises: 04ca088b8f21
Create Date: 2023-07-12 17:40:13.733915

"""

import datetime

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "203358c88297"
down_revision = "04ca088b8f21"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "ban",
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=str(datetime.datetime.now(tz=datetime.timezone.utc)),
        ),
    )


def downgrade() -> None:
    op.drop_column("ban", "created_at")
