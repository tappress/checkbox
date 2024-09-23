from datetime import datetime, timezone, timedelta

import jwt
from passlib.context import CryptContext
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from checkbox.database.models import User
from checkbox.dto.user import SignUpUserDto, TokensResponseDto, SignInUserDto
from checkbox.exceptions.base import Unauthorized, ResourceAlreadyExists
from checkbox.services.base import BaseService
from checkbox.config import Settings


class UserService(BaseService):

    def __init__(
        self, session: AsyncSession, settings: Settings, password_context: CryptContext
    ) -> None:
        super().__init__(session)
        self.settings = settings
        self.password_context = password_context

    async def sign_up(self, data: SignUpUserDto) -> TokensResponseDto:
        stmt = select(User).where(User.email == data.email)
        user = await self.session.scalar(stmt)

        if user:
            raise ResourceAlreadyExists(
                f"User with email {data.email} already registered"
            )

        user = await self.create(email=data.email, password=data.password)
        return self.generate_auth_tokens(user.id)

    async def sign_in(self, data: SignInUserDto) -> TokensResponseDto:
        stmt = select(User).where(User.email == data.email)
        user = await self.session.scalar(stmt)

        if not user:
            raise Unauthorized(f"Invalid email or password.")

        if not self.password_context.verify(secret=data.password, hash=user.password):
            raise Unauthorized(f"Invalid email or password.")

        return self.generate_auth_tokens(user.id)

    async def create(self, email: str, password: str) -> User:
        db_user = User(
            email=email,
            password=self.password_context.hash(password),
        )
        self.session.add(db_user)
        await self.session.commit()
        return db_user

    async def delete(self, user_id: int) -> None:
        stmt = delete(User).where(User.id == user_id)
        await self.session.execute(stmt)
        await self.session.commit()

    async def get_by_id(self, user_id: str) -> User:
        return await self.session.scalar(select(User).where(User.id == user_id))

    def generate_auth_tokens(self, user_id: str) -> TokensResponseDto:
        access_token = self._generate_access_token(user_id)
        refresh_token = self._generate_refresh_token(user_id)
        return TokensResponseDto(access_token=access_token, refresh_token=refresh_token)

    async def refresh_auth_tokens(self, refresh_token: str) -> TokensResponseDto:
        user_id = self._get_user_id_from_refresh_token(refresh_token)
        return self.generate_auth_tokens(user_id)

    def _generate_access_token(self, user_id: str) -> str:
        return jwt.encode(
            payload={
                "sub": user_id,
                "exp": datetime.now(tz=timezone.utc)
                + timedelta(minutes=self.settings.auth.ACCESS_TOKEN_EXPIRE_MINUTES),
            },
            key=self.settings.auth.ACCESS_TOKEN_SECRET_KEY,
            algorithm=self.settings.auth.ALGORITHM,
        )

    def _generate_refresh_token(self, user_id: str) -> str:
        return jwt.encode(
            payload={
                "sub": user_id,
                "exp": datetime.now(tz=timezone.utc)
                + timedelta(minutes=self.settings.auth.REFRESH_TOKEN_EXPIRE_MINUTES),
            },
            key=self.settings.auth.REFRESH_TOKEN_SECRET_KEY,
            algorithm=self.settings.auth.ALGORITHM,
        )

    def get_user_id_from_access_token(self, token: str) -> str:
        return self._get_user_id_from_token(
            token, self.settings.auth.ACCESS_TOKEN_SECRET_KEY
        )

    def _get_user_id_from_refresh_token(self, token: str) -> str:
        return self._get_user_id_from_token(
            token, self.settings.auth.REFRESH_TOKEN_SECRET_KEY
        )

    def _get_user_id_from_token(self, token: str, secret_key: str) -> str:
        try:
            decoded_token = jwt.decode(
                token, secret_key, algorithms=[self.settings.auth.ALGORITHM]
            )
        except jwt.PyJWTError:
            raise Unauthorized("Could not validate credentials")

        user_id = decoded_token.get("sub")

        if user_id is None:
            raise Unauthorized("Could not validate credentials")

        return user_id
