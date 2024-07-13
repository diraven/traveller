"""empty message

Revision ID: 8896f4eed972
Revises: cd7e29a8bb6e
Create Date: 2024-05-22 21:20:42.532004

"""

import sqlalchemy as sa
from sqlalchemy.orm import Session

from alembic import op
from models import BansSharingBan

revision = "8896f4eed972"
down_revision = "cd7e29a8bb6e"
branch_labels = None
depends_on = None


def upgrade() -> None:
    session = Session(op.get_bind())
    session.execute(sa.update(BansSharingBan).values(created_by=111508144135393280))
    session.commit()


def downgrade() -> None:
    session = Session(op.get_bind())
    session.execute(sa.update(BansSharingBan).values(created_by=None))
    session.commit()
