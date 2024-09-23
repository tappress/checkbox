from dishka import Provider, provide, Scope, from_context
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession

from checkbox.config import Settings
from checkbox.services.receipt_service import ReceiptService
from checkbox.services.user import UserService


class ServiceProvider(Provider):
    settings = from_context(provides=Settings, scope=Scope.APP)

    @provide(scope=Scope.REQUEST)
    async def get_user_service(
        self,
        settings: Settings,
        session: AsyncSession,
        password_context: CryptContext,
    ) -> UserService:
        return UserService(
            session=session, settings=settings, password_context=password_context
        )

    @provide(scope=Scope.REQUEST)
    async def get_receipt_service(
        self,
        session: AsyncSession,
    ) -> ReceiptService:
        return ReceiptService(session=session)
