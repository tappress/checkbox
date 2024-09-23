import pytest
import pytest_asyncio
from dishka import make_async_container, AsyncContainer
from httpx import AsyncClient, ASGITransport
from passlib.context import CryptContext
from pytest_asyncio import is_async_test
from sqlalchemy.ext.asyncio import AsyncSession

from checkbox.config import Settings
from checkbox.di import MainProvider, ServiceProvider
from checkbox.services.user import UserService
from checkbox.web.main import app


def pytest_collection_modifyitems(items):
    # Use the same event loop for all tests to avoid issues with SQLAlchemy
    # https://github.com/MagicStack/asyncpg/issues/863#issuecomment-1229220920
    pytest_asyncio_tests = (item for item in items if is_async_test(item))
    session_scope_marker = pytest.mark.asyncio(loop_scope="session")

    for async_test in pytest_asyncio_tests:
        async_test.add_marker(session_scope_marker, append=False)


@pytest_asyncio.fixture(scope="session")
def settings():
    return Settings()


@pytest_asyncio.fixture
async def pwd_context(di_container: AsyncContainer):
    return await di_container.get(CryptContext)


@pytest_asyncio.fixture(scope="session")
def di_container(settings):
    return make_async_container(
        MainProvider(), ServiceProvider(), context={Settings: settings}
    )


@pytest_asyncio.fixture()
async def db_session(di_container: AsyncContainer):
    async with di_container() as request_container:
        yield await request_container.get(AsyncSession)


@pytest_asyncio.fixture
async def user_service(di_container: AsyncContainer):
    async with di_container() as request_container:
        yield await request_container.get(UserService)


@pytest_asyncio.fixture
async def client():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac

