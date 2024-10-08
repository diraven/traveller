"""empty message

Revision ID: e16669881c74
Revises: d6e88eeaa282
Create Date: 2024-07-13 13:06:39.886179

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "e16669881c74"
down_revision = "d6e88eeaa282"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "bans_sharing_trusted_moderators",
        sa.Column("user_global_name", sa.String(length=32), nullable=False),
    )
    op.create_unique_constraint(
        op.f("uq_bans_sharing_trusted_moderators_guild_id"),
        "bans_sharing_trusted_moderators",
        ["guild_id", "user_id"],
    )
    op.create_unique_constraint(
        op.f("uq_bans_sharing_trusted_moderators_user_global_name"),
        "bans_sharing_trusted_moderators",
        ["user_global_name"],
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(
        op.f("uq_bans_sharing_trusted_moderators_user_global_name"),
        "bans_sharing_trusted_moderators",
        type_="unique",
    )
    op.drop_constraint(
        op.f("uq_bans_sharing_trusted_moderators_guild_id"),
        "bans_sharing_trusted_moderators",
        type_="unique",
    )
    op.drop_column("bans_sharing_trusted_moderators", "user_global_name")
    # ### end Alembic commands ###
