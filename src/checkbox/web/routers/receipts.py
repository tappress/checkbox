from datetime import datetime
from decimal import Decimal
from io import StringIO

from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, Query
from pydantic import NonNegativeInt, PositiveInt
from starlette import status
from starlette.responses import StreamingResponse

from checkbox.database.models import User
from checkbox.database.models.receipt import PaymentType
from checkbox.dto.generic import OffsetResponse
from checkbox.dto.receipt import CreateReceiptDto, ReceiptDto
from checkbox.services.receipt_service import ReceiptService

router = APIRouter(prefix="/receipts", route_class=DishkaRoute, tags=["Receipt"])


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_receipt(
    user: FromDishka[User],
    data: CreateReceiptDto,
    receipt_service: FromDishka[ReceiptService],
) -> ReceiptDto:
    return await receipt_service.create(data, user_id=user.id)


@router.get("")
async def get_all_user_receipts(
    user: FromDishka[User],
    receipt_service: FromDishka[ReceiptService],
    start_date: datetime = Query(None),
    end_date: datetime = Query(None),
    payment_type: PaymentType = Query(None),
    min_total: Decimal = Query(None),
    offset: NonNegativeInt = Query(0),
    limit: PositiveInt = Query(100),
) -> OffsetResponse[ReceiptDto]:
    return await receipt_service.get_user_receipts(
        user_id=user.id,
        start_date=start_date,
        end_date=end_date,
        payment_type=payment_type,
        min_total=min_total,
        offset=offset,
        limit=limit,
    )


@router.get("/{receipt_id}")
async def get_receipt_by_id(
    user: FromDishka[User],
    receipt_id: str,
    receipt_service: FromDishka[ReceiptService],
) -> ReceiptDto:
    return await receipt_service.get_user_receipt_by_id(
        receipt_id=receipt_id,
        user_id=user.id,
    )


@router.get("/{receipt_id}/plaintext")
async def get_plaintext_receipt(
    receipt_service: FromDishka[ReceiptService],
    receipt_id: str,
    line_length: int = Query(32, ge=20, le=50),
) -> str:
    return await receipt_service.get_plaintext_receipt(
        receipt_id=receipt_id, line_length=line_length
    )


@router.get("/{receipt_id}/plaintext/download")
async def download_plaintext_receipt(
    receipt_service: FromDishka[ReceiptService],
    receipt_id: str,
    line_length: int = Query(32, ge=20, le=50),
) -> StreamingResponse:
    formatted_receipt = await receipt_service.get_plaintext_receipt(
        receipt_id=receipt_id, line_length=line_length
    )

    receipt_file = StringIO(formatted_receipt)
    receipt_filename = f"receipt_{receipt_id}.txt"

    return StreamingResponse(
        receipt_file,
        media_type="text/plain",
        headers={"Content-Disposition": f"attachment; filename={receipt_filename}"},
    )
