import sqlalchemy as sa
from sqlalchemy.orm import DeclarativeBase

engine = sa.create_engine("sqlite:///.data.sqlite", echo=True)


class Base(DeclarativeBase):  # pylint: disable=too-few-public-methods
    pass


class Guild(Base):  # pylint: disable=too-few-public-methods
    __tablename__ = "guild"
    id: int = sa.Column(sa.Integer, primary_key=True)  # type: ignore
    name: str = sa.Column(sa.String(100), nullable=False)  # type: ignore
    log_channel_id: int = sa.Column(sa.Integer, nullable=True)  # type: ignore

    def __repr__(self) -> str:
        return f"Guild(id={self.id}, name={self.name})"


# class Address(Base):
#     __tablename__ = "address"
#     id: Mapped[int] = mapped_column(primary_key=True)
#     email_address: Mapped[str]
#     user_id: Mapped[int] = mapped_column(ForeignKey("user_account.id"))
#     user: Mapped["User"] = relationship(back_populates="addresses")
#     def __repr__(self) -> str:
#         return f"Address(id={self.id!r}, email_address={self.email_address!r})"
