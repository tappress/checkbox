from typing import AsyncIterable

from dishka import Provider, provide, Scope, FromDishka, from_context
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker, AsyncSession

from checkbox.config import Settings
from checkbox.database.setup import create_sa_engine, create_sa_sessionmaker


class MainProvider(Provider):
    settings = from_context(provides=Settings, scope=Scope.APP)

    @provide(scope=Scope.APP)
    async def get_sa_engine(self, settings: Settings) -> AsyncIterable[AsyncEngine]:
        engine = create_sa_engine(
            postgres_url=settings.postgres.url, echo=settings.sqlalchemy.ECHO
        )

        yield engine

        await engine.dispose()

    @provide(scope=Scope.APP)
    def get_sa_sessionmaker(
        self, engine: FromDishka[AsyncEngine]
    ) -> async_sessionmaker:
        return create_sa_sessionmaker(engine)

    @provide(scope=Scope.REQUEST)
    async def get_sa_session(
        self, sa_sessionmaker: FromDishka[async_sessionmaker]
    ) -> AsyncIterable[AsyncSession]:
        async with sa_sessionmaker() as session:
            yield session

    @provide(scope=Scope.APP)
    def get_password_context(self) -> CryptContext:
        return CryptContext(schemes=["bcrypt"], deprecated="auto")
