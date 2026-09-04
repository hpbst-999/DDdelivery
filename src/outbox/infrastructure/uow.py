from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from src.outbox.infrastructure.postgres_repository import SQLAlchemyOutboxRepository

class SQLAlchemyUnitOfWork:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.outbox = SQLAlchemyOutboxRepository(self.session)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            await self.rollback()
        else:
            await self.commit()

    async def commit(self):
        await self.session.commit()

    async def rollback(self):
        await self.session.rollback()