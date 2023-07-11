import typing as t

import sqlalchemy as sa
import sqlalchemy.orm as sa_orm

engine = sa.create_engine("sqlite:///.data.sqlite", echo=True)


class Base(sa_orm.DeclarativeBase):  # pylint: disable=too-few-public-methods
    pass


class Guild(Base):  # pylint: disable=too-few-public-methods
    __tablename__ = "guild"
    id: sa_orm.Mapped[int] = sa_orm.mapped_column(primary_key=True)
    name: sa_orm.Mapped[t.Optional[str]] = sa_orm.mapped_column(sa.String(100))
    bans_sharing_channel_id: sa_orm.Mapped[t.Optional[int]] = sa_orm.mapped_column()
    verification_role_id: sa_orm.Mapped[t.Optional[int]] = sa_orm.mapped_column()

    def __repr__(self) -> str:
        return f"Guild(id={self.id}, name={self.name})"


class KnownBan(Base):  # pylint: disable=too-few-public-methods
    __tablename__ = "ban"
    id: sa_orm.Mapped[int] = sa_orm.mapped_column(primary_key=True)
    reason: sa_orm.Mapped[t.Optional[str]] = sa_orm.mapped_column(sa.String(500))

    def __repr__(self) -> str:
        return f"KnownBan(user_id={self.id}, reason={self.reason})"
