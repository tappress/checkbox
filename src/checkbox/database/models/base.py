from datetime import datetime
from decimal import Decimal
from typing import Annotated

from sqlalchemy import TIMESTAMP, VARCHAR, ForeignKey, DECIMAL
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped, mapped_column
from ulid import ULID

PkColumn = Annotated[
    str,
    mapped_column(VARCHAR(26), primary_key=True, default=lambda: str(ULID())),
]

MoneyColumn = Annotated[Decimal, mapped_column(DECIMAL(10, 2))]


class Base(AsyncAttrs, DeclarativeBase):
    pass


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), default=func.now(), onupdate=func.now()
    )


class CascadingForeignKey(ForeignKey):

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs, ondelete="cascade", onupdate="cascade")
