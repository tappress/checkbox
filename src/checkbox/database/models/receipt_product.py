from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin, PkColumn, CascadingForeignKey, MoneyColumn


class ReceiptProduct(Base, TimestampMixin):
    __tablename__ = "receipt_products"

    id: Mapped[PkColumn]
    receipt_id: Mapped[str] = mapped_column(CascadingForeignKey("receipts.id"))
    name: Mapped[str]
    price: Mapped[MoneyColumn]
    quantity: Mapped[int]
    total: Mapped[MoneyColumn]

    receipt: Mapped[list["Reciept"]] = relationship(
        "Receipt", back_populates="products"
    )
