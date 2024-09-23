from datetime import datetime, timedelta, UTC
from decimal import Decimal

import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from checkbox.database.models import Receipt, User
from checkbox.database.models.receipt import PaymentType
from checkbox.services.user import UserService


@pytest_asyncio.fixture()
async def test_user(db_session: AsyncSession, user_service: UserService):
    user = await user_service.create(
        email="test_cashier@gmail.com", password="securepassword"
    )

    yield user

    await user_service.delete(user.id)


@pytest_asyncio.fixture()
async def access_token(client: AsyncClient, test_user: User) -> str:
    sign_in_data = {"email": "test_cashier@gmail.com", "password": "securepassword"}
    response = await client.post("/users/sign-in", json=sign_in_data)
    tokens = response.json()
    return tokens["access_token"]


async def test_create_receipt(
    client: AsyncClient, db_session: AsyncSession, test_user: User, access_token: str
):
    invalid_receipt_data = {
        "products": [
            {"name": "Product 1", "price": "10.50", "quantity": 2},
            {"name": "Product 2", "price": "5.00", "quantity": 1},
        ],
        "payment": {"type": "CASH", "amount": "10.00"},  # invalid amount
    }
    receipt_data = {
        "products": [
            {"name": "Product 1", "price": "10.50", "quantity": 2},
            {"name": "Product 2", "price": "5.00", "quantity": 1},
        ],
        "payment": {"type": "CASH", "amount": "26.00"},
    }

    response = await client.post(
        "/receipts",
        json=receipt_data,
    )
    assert response.status_code == 401

    response = await client.post(
        "/receipts",
        json=invalid_receipt_data,
        headers={"Authorization": f"Bearer {access_token}"},
    )
    error = response.json()
    assert error["code"] == "PAYMENT_AMOUNT_MISMATCH"

    response = await client.post(
        "/receipts",
        json=receipt_data,
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 201, response.text
    receipt = response.json()

    db_receipt = await db_session.scalar(
        select(Receipt)
        .options(joinedload(Receipt.products))
        .where(Receipt.id == receipt["id"])
    )
    assert db_receipt is not None
    assert db_receipt.user_id == test_user.id
    assert len(db_receipt.products) == 2


async def test_get_receipt_by_id(
    client: AsyncClient, db_session: AsyncSession, test_user: User, access_token: str
):
    receipt = Receipt(
        user_id=test_user.id,
        payment_type=PaymentType.CASH,
        payment_amount=Decimal("50.00"),
        total=Decimal("50.00"),
        rest=Decimal("0.00"),
    )
    db_session.add(receipt)
    await db_session.commit()

    response = await client.get(
        f"/receipts/{receipt.id}", headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == 200, response.text

    fetched_receipt = response.json()
    assert fetched_receipt["id"] == str(receipt.id)
    assert fetched_receipt["payment"]["amount"] == "50.00"


async def test_get_receipt_by_invalid_id(
    client: AsyncClient, db_session: AsyncSession, test_user: User, access_token: str
):
    response = await client.get(
        "/receipts/invalid_receipt_id",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 404
    assert "not found" in response.text.lower()


async def test_get_receipts_with_filters(
    client: AsyncClient, db_session: AsyncSession, test_user: User, access_token: str
):
    receipt1 = Receipt(
        user_id=test_user.id,
        payment_type=PaymentType.CASH,
        payment_amount=Decimal("50.00"),
        total=Decimal("40.00"),
        rest=Decimal("10.00"),
        created_at=datetime.now(tz=UTC) - timedelta(days=5),
    )
    receipt2 = Receipt(
        user_id=test_user.id,
        payment_type=PaymentType.CARD,
        payment_amount=Decimal("60.00"),
        total=Decimal("60.00"),
        rest=Decimal("0.00"),
        created_at=datetime.now(tz=UTC) - timedelta(days=2),
    )
    db_session.add_all([receipt1, receipt2])
    await db_session.commit()

    response = await client.get(
        "/receipts",
        headers={"Authorization": f"Bearer {access_token}"},
        params={"payment_type": "CASH"},
    )
    assert response.status_code == 200
    receipts = response.json()
    assert len(receipts["items"]) == 1
    assert receipts["items"][0]["payment"]["type"] == "CASH"

    start_date = (datetime.now(tz=UTC) - timedelta(days=6)).isoformat()
    end_date = (datetime.now(tz=UTC) - timedelta(days=3)).isoformat()
    response = await client.get(
        f"/receipts",
        headers={"Authorization": f"Bearer {access_token}"},
        params={
            "start_date": start_date,
            "end_date": end_date,
        },
    )
    assert response.status_code == 200, response.text
    receipts = response.json()
    assert len(receipts["items"]) == 1
    assert receipts["items"][0]["id"] == str(receipt1.id)

    response = await client.get(
        "/receipts",
        headers={"Authorization": f"Bearer {access_token}"},
        params={"min_total": "50.00"},
    )
    assert response.status_code == 200
    receipts = response.json()
    assert len(receipts["items"]) == 1
    assert receipts["items"][0]["total"] == "60.00"


async def test_get_receipts_with_pagination(
    client: AsyncClient, db_session: AsyncSession, test_user: User, access_token: str
):
    for i in range(5):
        receipt = Receipt(
            user_id=test_user.id,
            payment_type=PaymentType.CARD,
            payment_amount=Decimal(f"{50 + i}.00"),
            total=Decimal(f"{50 + i}.00"),
            rest=Decimal("0.00"),
            created_at=datetime.utcnow() - timedelta(days=i),
        )
        db_session.add(receipt)
    await db_session.commit()

    response = await client.get(
        "/receipts?offset=0&limit=2",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 200
    receipts = response.json()
    assert len(receipts["items"]) == 2
    assert receipts["total"] == 5

    response = await client.get(
        "/receipts?offset=2&limit=2",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 200
    receipts = response.json()
    assert len(receipts["items"]) == 2

    response = await client.get(
        "/receipts?offset=4&limit=2",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 200
    receipts = response.json()
    assert len(receipts["items"]) == 1


async def test_plaintext_receipt_structure_and_accessibility(
    client: AsyncClient, db_session: AsyncSession, test_user: User, access_token: str
):
    receipt_data = {
        "products": [
            {"name": "Product 1", "price": "10.50", "quantity": 2},
            {"name": "Product 2", "price": "5.00", "quantity": 1},
        ],
        "payment": {"type": "CASH", "amount": "26.00"},
    }

    response = await client.post(
        "/receipts",
        json=receipt_data,
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 201, response.text
    receipt = response.json()

    response = await client.get(
        f"/receipts/{receipt['id']}/plaintext",
        params={"line_length": 32},
    )
    assert response.status_code == 200, response.text

    plaintext_receipt = response.text
    assert "Product 1" in plaintext_receipt
    assert "2.00 x 10.50" in plaintext_receipt
    assert "26.00" in plaintext_receipt
    assert "Дякуємо за покупку!" in plaintext_receipt
