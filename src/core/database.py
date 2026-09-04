from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase
from src.core.config import settings

engine:AsyncEngine = create_async_engine(
    url=settings.database_url, 
    echo=True,
    pool_pre_ping=True,
    pool_size=5,       
    max_overflow=10  
)

SessionFactory:AsyncSession = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    autocommit=False, 
    autoflush=False, 
    expire_on_commit=False
)

class Base(DeclarativeBase):
    pass


async def init_db() -> None:

    from src.identity.infrastructure.models import (
        AccountModel, 
        UserProfileModel, 
        CourierProfileModel,
        OTPModel,
        RefreshTokenModel
    )
    from src.outbox.infrastructure.models import OutboxMessageModel

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
