from collections.abc import AsyncGenerator

import pytest_asyncio
from sqlalchemy.ext.asyncio import (
    AsyncConnection,
    AsyncEngine,
    AsyncSession,
    create_async_engine,
)

from src.core.config import settings
from src.courier.infrastructure.postgres_repositories import SQLAlchemyCourierProfileRepository
from src.courier.infrastructure.uow import UnitOfWork


@pytest_asyncio.fixture
async def engine() -> AsyncGenerator[AsyncEngine, None]:
    test_engine = create_async_engine(settings.database_url)
    yield test_engine
    await test_engine.dispose()


@pytest_asyncio.fixture
async def connection(engine: AsyncEngine) -> AsyncGenerator[AsyncConnection, None]:
    async with engine.connect() as conn:
        trans = await conn.begin()
        try:
            yield conn
        finally:
            await trans.rollback()


@pytest_asyncio.fixture
async def session(connection: AsyncConnection) -> AsyncGenerator[AsyncSession, None]:
    async_session = AsyncSession(
        bind=connection,
        join_transaction_mode="create_savepoint",
        expire_on_commit=False,
    )
    try:
        yield async_session
    finally:
        await async_session.close()


@pytest_asyncio.fixture
async def courier_repo(session: AsyncSession) -> SQLAlchemyCourierProfileRepository:
    return SQLAlchemyCourierProfileRepository(session=session)


@pytest_asyncio.fixture
async def uow(session: AsyncSession) -> UnitOfWork:
    return UnitOfWork(session=session)