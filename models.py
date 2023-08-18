import datetime
import typing as t

import sqlalchemy as sa
import sqlalchemy.orm as sa_orm

engine = sa.create_engine("sqlite:///.data.sqlite", echo=True)


class Base(sa_orm.DeclarativeBase):
    pass


class Guild(Base):
    __tablename__ = "guild"
    id: sa_orm.Mapped[int] = sa_orm.mapped_column(primary_key=True)
    name: sa_orm.Mapped[t.Optional[str]] = sa_orm.mapped_column(sa.String(100))
    bans_sharing_channel_id: sa_orm.Mapped[t.Optional[int]] = sa_orm.mapped_column()
    verification_role_id: sa_orm.Mapped[t.Optional[int]] = sa_orm.mapped_column()

    def __repr__(self) -> str:
        return f"Guild(id={self.id}, name={self.name})"


class KnownBan(Base):
    __tablename__ = "ban"
    id: sa_orm.Mapped[int] = sa_orm.mapped_column(primary_key=True)
    created_at: sa_orm.Mapped[datetime.datetime] = sa_orm.mapped_column(
        sa.types.DateTime(timezone=True), default=datetime.datetime.utcnow
    )
    reason: sa_orm.Mapped[t.Optional[str]] = sa_orm.mapped_column(sa.String(500))

    def __repr__(self) -> str:
        return f"KnownBan(member_id={self.id}, reason={self.reason})"
