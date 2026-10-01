from types import TracebackType
from typing import Self

from sqlalchemy.ext.asyncio import AsyncSession

from src.courier.application.interfaces import ICourierProfileRepository
from src.courier.infrastructure.postgres_repositories import SQLAlchemyCourierProfileRepository


class SQLAlchemyUnitOfWork:
    courier_profiles: ICourierProfileRepository

    def __init__(self, session: AsyncSession) -> None:
        self.session: AsyncSession = session

    async def __aenter__(self) -> Self:
        self.courier_profiles = SQLAlchemyCourierProfileRepository(self.session)
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        if exc_type:
            await self.rollback()
        else:
            await self.commit()

    async def commit(self) -> None:
        await self.session.commit()

    async def rollback(self) -> None:
        await self.session.rollback()
