from typing import Self

from sqlalchemy.ext.asyncio import AsyncSession

from src.identity.infrastructure.postgres_repositories import (
    SQLAlchemyAccountRepository,
    SQLAlchemyOTPRepository,
    SQLAlchemyRefreshTokenRepository,
    SQLAlchemyUserProfileRepository,
)
from src.outbox.infrastructure.postgres_repository import SQLAlchemyOutboxRepository


class UnitOfWork:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def __aenter__(self) -> Self:
        self.otp = SQLAlchemyOTPRepository(self.session)
        self.accounts = SQLAlchemyAccountRepository(self.session)
        self.user_profiles = SQLAlchemyUserProfileRepository(self.session)
        self.refresh_tokens = SQLAlchemyRefreshTokenRepository(self.session)
        self.outbox = SQLAlchemyOutboxRepository(self.session)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        if exc_type:
            await self.rollback()
        else:
            await self.commit()

    async def commit(self) -> None:
        await self.session.commit()

    async def rollback(self) -> None:
        await self.session.rollback()
