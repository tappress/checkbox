from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin, PkColumn


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[PkColumn]
    email: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str]

    receipts: Mapped[list["Receipt"]] = relationship("Receipt", back_populates="user")
