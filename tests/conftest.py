import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import close_all_sessions

from src.models import Base


@pytest.fixture()
def anyio_backend():
    return "asyncio"


@pytest_asyncio.fixture(scope="session")
async def connection():
    engine = create_async_engine(url="sqlite+aiosqlite:///:memory:", echo=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()
    close_all_sessions()


@pytest_asyncio.fixture
async def dbsession(connection):
    async with AsyncSession(
        bind=connection,
        join_transaction_mode="create_savepoint",
        expire_on_commit=False,
    ) as session:
        yield session
