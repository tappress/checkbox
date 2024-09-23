from httpx import AsyncClient
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from checkbox.database.models import User
from checkbox.services.user import UserService


async def test_sign_up(db_session: AsyncSession, client: AsyncClient):
    sign_up_data = {"email": "test1@gmail.com", "password": "securepassword"}

    response = await client.post("/users/sign-up", json=sign_up_data)

    assert response.status_code == 200
    tokens = response.json()

    assert "access_token" in tokens
    assert "refresh_token" in tokens

    user = await db_session.scalar(
        select(User).where(User.email == sign_up_data["email"])
    )
    assert user is not None
    assert user.email == sign_up_data["email"]


async def test_sign_in(
    db_session: AsyncSession, pwd_context: CryptContext, client: AsyncClient
):
    user = User(email="test2@gmail.com", password=pwd_context.hash("securepassword"))
    db_session.add(user)
    await db_session.commit()

    sign_in_data = {"email": "test2@gmail.com", "password": "securepassword"}
    response = await client.post("/users/sign-in", json=sign_in_data)
    assert response.status_code == 200, response.text
    tokens = response.json()

    assert "access_token" in tokens
    assert "refresh_token" in tokens


async def test_refresh_tokens(
    db_session: AsyncSession,
    user_service: UserService,
    pwd_context: CryptContext,
    client: AsyncClient,
):
    user = User(email="test3@gmail.com", password=pwd_context.hash("securepassword"))
    db_session.add(user)
    await db_session.commit()

    tokens = user_service.generate_auth_tokens(user.id)
    refresh_data = {"refresh_token": tokens.refresh_token}
    response = await client.post("/users/refresh-tokens", json=refresh_data)

    assert response.status_code == 200, response.text
    new_tokens = response.json()

    assert "access_token" in new_tokens
    assert "refresh_token" in new_tokens
