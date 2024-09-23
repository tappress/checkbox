from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, model_validator

from checkbox.database.models.receipt import PaymentType, Receipt


class CreateReceiptProductDto(BaseModel):
    name: str
    price: Decimal
    quantity: int


class CreateReceiptPaymentDto(BaseModel):
    type: PaymentType
    amount: Decimal


class CreateReceiptDto(BaseModel):
    products: list[CreateReceiptProductDto]
    payment: CreateReceiptPaymentDto


class ReceiptProductDto(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str
    price: Decimal
    quantity: int
    total: Decimal


class ReceiptPaymentDto(BaseModel):
    type: PaymentType
    amount: Decimal


class ReceiptDto(BaseModel):
    id: str
    products: list[ReceiptProductDto]
    total: Decimal
    payment: ReceiptPaymentDto
    rest: Decimal
    created_at: datetime

    @model_validator(mode="before")
    def parse_from_orm(cls, obj):
        if type(obj) is Receipt:
            return {
                "id": obj.id,
                "products": obj.products,
                "total": obj.total,
                "payment": {"amount": obj.payment_amount, "type": obj.payment_type},
                "rest": obj.rest,
                "created_at": obj.created_at,
            }

        return obj
