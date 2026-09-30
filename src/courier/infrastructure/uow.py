from sqlalchemy.ext.asyncio import AsyncSession

from src.courier.infrastructure.postgres_repositories import SQLAlchemyCourierProfileRepository


class SQLAlchemyUnitOfWork:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def __aenter__(self):
        self.courier_profiles = SQLAlchemyCourierProfileRepository(self.session)
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
