import uuid
from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncEngine, AsyncSession, create_async_engine

from src.core.config import settings
from src.identity.infrastructure.postgres_repositories import (
    SQLAlchemyAccountRepository,
    SQLAlchemyOTPRepository,
    SQLAlchemyRefreshTokenRepository,
    SQLAlchemyUserProfileRepository,
)
from src.identity.infrastructure.redis_repositories import RedisCacheRepository
from src.identity.infrastructure.security_jwt import JwtTokenService
from src.identity.infrastructure.uow import SQLAlchemyUnitOfWork

# These tests run against the real Postgres instance configured via settings
# (the same database the app itself uses in dev - see .env). Every test gets
# its own outer transaction that is rolled back in the `connection` fixture's
# teardown, so nothing written during a test is ever actually persisted.


@pytest_asyncio.fixture
async def engine() -> AsyncGenerator[AsyncEngine, None]:
    # Function-scoped (not session-scoped) on purpose: pytest-asyncio gives
    # each test its own event loop by default, and an asyncpg connection
    # pool created on one loop cannot be reused from another.
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
    # join_transaction_mode="create_savepoint" means the use-case/UoW calling
    # session.commit() only releases a SAVEPOINT, leaving the outer
    # transaction (and therefore the rollback above) in control.
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
async def uow(session: AsyncSession) -> SQLAlchemyUnitOfWork:
    return SQLAlchemyUnitOfWork(session=session)


@pytest_asyncio.fixture
async def account_repo(session: AsyncSession) -> SQLAlchemyAccountRepository:
    return SQLAlchemyAccountRepository(session)


@pytest_asyncio.fixture
async def profile_repo(session: AsyncSession) -> SQLAlchemyUserProfileRepository:
    return SQLAlchemyUserProfileRepository(session)


@pytest_asyncio.fixture
async def otp_repo(session: AsyncSession) -> SQLAlchemyOTPRepository:
    return SQLAlchemyOTPRepository(session)


@pytest_asyncio.fixture
async def refresh_token_repo(session: AsyncSession) -> SQLAlchemyRefreshTokenRepository:
    return SQLAlchemyRefreshTokenRepository(session)


@pytest_asyncio.fixture
async def token_service() -> JwtTokenService:
    return JwtTokenService(secret_key=settings.JWT_SECRET_KEY)


@pytest_asyncio.fixture
async def redis_client() -> AsyncGenerator[Redis, None]:
    client = Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=settings.REDIS_DB)
    try:
        yield client
    finally:
        # Every key used by these tests is created via the `cache_key` fixture
        # below under the "itest:" prefix, so sweeping that pattern can never
        # touch real app keys.
        cursor = 0
        while True:
            cursor, keys = await client.scan(cursor=cursor, match="itest:*")
            if keys:
                await client.delete(*keys)
            if cursor == 0:
                break
        await client.aclose()


@pytest_asyncio.fixture
async def cache_repo(redis_client: Redis) -> RedisCacheRepository:
    return RedisCacheRepository(redis_client=redis_client)


@pytest.fixture
def cache_key() -> str:
    return f"itest:{uuid.uuid4()}:user_profile"
