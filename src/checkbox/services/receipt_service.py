from datetime import datetime
from decimal import Decimal
from zoneinfo import ZoneInfo

from pydantic import TypeAdapter
from sqlalchemy import select, func
from sqlalchemy.orm import joinedload

from checkbox.database.models import ReceiptProduct, Receipt
from checkbox.database.models.receipt import PaymentType
from checkbox.dto.generic import OffsetResponse
from checkbox.dto.receipt import CreateReceiptDto, ReceiptDto
from checkbox.exceptions.base import NotFound, InvalidOffset
from checkbox.exceptions.receipts import PaymentAmountMismatch
from checkbox.services.base import BaseService


class ReceiptService(BaseService):

    async def create(self, data: CreateReceiptDto, user_id: str) -> ReceiptDto:
        receipt_products = []
        receipt_total = Decimal(0)

        for p in data.products:
            product_total = p.quantity * p.price
            receipt_total += product_total

            product = ReceiptProduct(
                name=p.name,
                quantity=p.quantity,
                price=p.price,
                total=product_total,
            )
            receipt_products.append(product)

        if data.payment.amount < receipt_total:
            raise PaymentAmountMismatch(
                f"Amount to pay: {receipt_total}. Amount paid: {data.payment.amount}"
            )

        rest = data.payment.amount - receipt_total

        recept = Receipt(
            user_id=user_id,
            products=receipt_products,
            payment_type=data.payment.type,
            payment_amount=data.payment.amount,
            total=receipt_total,
            rest=rest,
        )
        self.session.add(recept)
        await self.session.commit()

        return await self.get_user_receipt_by_id(receipt_id=recept.id, user_id=user_id)

    async def get_user_receipt_by_id(self, receipt_id: str, user_id: str) -> ReceiptDto:
        stmt = (
            select(Receipt)
            .options(joinedload(Receipt.products))
            .where(Receipt.id == receipt_id, Receipt.user_id == user_id)
        )
        receipt = await self.session.scalar(stmt)

        if not receipt:
            raise NotFound(f"Receipt (id={receipt_id}) not found")

        return ReceiptDto.model_validate(receipt)

    async def get_user_receipts(
        self,
        user_id: str,
        start_date: datetime | None,
        end_date: datetime | None,
        payment_type: PaymentType | None,
        min_total: Decimal | None,
        offset: int,
        limit: int,
    ) -> OffsetResponse[ReceiptDto]:
        count_stmt = select(func.count()).where(Receipt.user_id == user_id)
        items_stmt = (
            select(Receipt)
            .options(joinedload(Receipt.products))
            .where(Receipt.user_id == user_id)
            .offset(offset)
            .limit(limit)
        )

        if start_date:
            count_stmt = count_stmt.where(Receipt.created_at >= start_date)
            items_stmt = items_stmt.where(Receipt.created_at >= start_date)

        if end_date:
            count_stmt = count_stmt.where(Receipt.created_at <= end_date)
            items_stmt = items_stmt.where(Receipt.created_at <= end_date)

        if payment_type:
            count_stmt = count_stmt.where(Receipt.payment_type == payment_type)
            items_stmt = items_stmt.where(Receipt.payment_type == payment_type)

        if min_total:
            count_stmt = count_stmt.where(Receipt.total >= min_total)
            items_stmt = items_stmt.where(Receipt.total >= min_total)

        total_count = await self.session.scalar(count_stmt)
        max_offset = total_count - 1

        if offset > max_offset:
            raise InvalidOffset(f"Max offset value is {max_offset}")

        result = await self.session.execute(items_stmt)
        receipts = result.unique().scalars()
        items = TypeAdapter(list[ReceiptDto]).validate_python(receipts)

        return OffsetResponse[ReceiptDto](items=items, total=total_count)

    async def get_plaintext_receipt(self, receipt_id: str, line_length: int) -> str:
        stmt = (
            select(Receipt)
            .options(joinedload(Receipt.products))
            .where(Receipt.id == receipt_id)
        )
        receipt = await self.session.scalar(stmt)

        if not receipt:
            raise NotFound(f"Receipt (id={receipt_id}) not found")

        return self.format_receipt(receipt, line_length)

    @staticmethod
    def format_receipt(receipt: Receipt, line_length: int = 32) -> str:
        receipt_lines = [f"{'checkbox.ua':^{line_length}}", "=" * line_length]

        for product in receipt.products:
            quantity_price = f"{product.quantity:.2f} x {product.price:,.2f}".rjust(
                line_length - len(product.name)
            )
            receipt_lines.append(
                f"{product.name.ljust(line_length - len(quantity_price))}{quantity_price}"
            )
            total = f"{product.total:,.2f}".rjust(line_length)
            receipt_lines.append(total)

        receipt_lines.append("=" * line_length)

        str_total = str(receipt.total)
        receipt_lines.append(f"СУМА{str_total:>{line_length - len(str_total) + 1}}")

        str_payment_amount = str(receipt.payment_amount)
        receipt_lines.append(
            f"{receipt.payment_type.capitalize()}{str_payment_amount:>{line_length - len(str_payment_amount) + 1}}"
        )
        str_rest = str(receipt.rest)
        receipt_lines.append(f"Решта{str_rest:>{line_length - len(str_rest) - 1}}")
        receipt_lines.append("=" * line_length)

        kyiv_tz = ZoneInfo("Europe/Kyiv")
        created_at_kyiv = receipt.created_at.astimezone(kyiv_tz)
        receipt_lines.append(
            f"{created_at_kyiv.strftime('%d.%m.%Y %H:%M'):^{line_length}}"
        )
        receipt_lines.append(f"{'Дякуємо за покупку!':^{line_length}}")

        return "\n".join(receipt_lines)
