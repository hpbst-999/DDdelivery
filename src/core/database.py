from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from src.core.config import settings
from redis.asyncio import Redis
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass

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


redis_client = Redis(
    host=settings.REDIS_HOST, 
    port=settings.REDIS_PORT, 
    db=settings.REDIS_DB,
    decode_responses=True
)
