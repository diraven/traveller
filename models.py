import datetime
import os
import typing as t

import discord
import sqlalchemy as sa
import sqlalchemy.orm as sa_orm
from discord.ext import commands


DB_URL = f'postgresql+psycopg://postgres:{os.environ["POSTGRES_PASSWORD"]}@{os.environ["PGHOST"]}:5432/postgres'
engine = sa.create_engine(DB_URL)
Session = sa_orm.sessionmaker(engine)


class Base(sa_orm.DeclarativeBase):
    pass


class Guild(Base):
    __tablename__ = "guilds"
    id_: sa_orm.Mapped[int] = sa_orm.mapped_column(sa.BigInteger, primary_key=True)
    name: sa_orm.Mapped[t.Optional[str]] = sa_orm.mapped_column(sa.String(100))
    bans_sharing_channel_id: sa_orm.Mapped[t.Optional[int]] = sa_orm.mapped_column(
        sa.BigInteger
    )
    verification_role_id: sa_orm.Mapped[t.Optional[int]] = sa_orm.mapped_column(
        sa.BigInteger
    )

    def __repr__(self) -> str:
        return f"Guild(id_={self.id_}, name={self.name})"

    def get_bans_sharing_channel(self, bot: commands.Bot) -> discord.TextChannel:
        if not self.bans_sharing_channel_id:
            raise (
                RuntimeError(f"Bans sharing channel id not found for guild {self.id_}")
            )
        return t.cast(
            discord.TextChannel, bot.get_channel(self.bans_sharing_channel_id)
        )


class BansSharingTrustedModerator(Base):
    __tablename__ = "bans_sharing_trusted_moderators"
    id_: sa_orm.Mapped[int] = sa_orm.mapped_column(sa.BigInteger, primary_key=True)
    created_at: sa_orm.Mapped[datetime.datetime] = sa_orm.mapped_column(
        sa.types.DateTime(timezone=True),
        default=datetime.datetime.now(tz=datetime.timezone.utc),
    )
    created_by: sa_orm.Mapped[int] = sa_orm.mapped_column(sa.BigInteger)
    guild_id: sa_orm.Mapped[int] = sa_orm.mapped_column(sa.BigInteger)
    user_id: sa_orm.Mapped[int] = sa_orm.mapped_column(sa.BigInteger)

    def __repr__(self) -> str:
        return f"BansSharingTrustedModerator(created_by={self.created_by}, guild_id={self.guild_id}, user_id={self.user_id})"


class BansSharingBan(Base):
    __tablename__ = "bans_sharing_bans"
    id_: sa_orm.Mapped[int] = sa_orm.mapped_column(
        sa.BigInteger,
        primary_key=True,
    )
    created_at: sa_orm.Mapped[datetime.datetime] = sa_orm.mapped_column(
        sa.types.DateTime(timezone=True),
        default=datetime.datetime.now(tz=datetime.timezone.utc),
    )
    created_by: sa_orm.Mapped[int] = sa_orm.mapped_column(sa.BigInteger)
    reason: sa_orm.Mapped[t.Optional[str]] = sa_orm.mapped_column(sa.String(500))

    def __repr__(self) -> str:
        return f"BansSharingBan(member_id={self.id_}, reason={self.reason})"


class Bot(commands.Bot):
    def get_guild_config(self, session: sa_orm.Session, id_: int) -> Guild:
        statement = sa.select(Guild).filter_by(id_=id_)
        return session.execute(statement).scalar_one()


class Cog(commands.Cog):
    def __init__(self, bot: Bot):
        self.bot: Bot = bot
