from enum import StrEnum

from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import (
    Base,
    TimestampMixin,
    PkColumn,
    CascadingForeignKey,
    MoneyColumn,
)


class PaymentType(StrEnum):
    CASH = "CASH"
    CARD = "CARD"


class Receipt(Base, TimestampMixin):
    __tablename__ = "receipts"

    id: Mapped[PkColumn]
    user_id: Mapped[str] = mapped_column(CascadingForeignKey("users.id"))
    total: Mapped[MoneyColumn]
    payment_type: Mapped[PaymentType]
    payment_amount: Mapped[MoneyColumn]
    rest: Mapped[MoneyColumn]

    user: Mapped["User"] = relationship("User", back_populates="receipts")
    products: Mapped[list["ReceiptProduct"]] = relationship(
        "ReceiptProduct", back_populates="receipt"
    )
