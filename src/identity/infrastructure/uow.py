# import redis
# from src.identity.application.interfaces import IUnitOfWork
# from src.identity.infrastructure.redis_repositories import RedisSessionRepository
from src.identity.infrastructure.postgres_repositories import (
    SQLAlchemyAccountRepository,
    SQLAlchemyUserProfileRepository,
    SQLAlchemyCourierProfileRepository,
    SQLAlchemyOTPRepository,
    SQLAlchemyRefreshTokenRepository
)
from sqlalchemy.orm import Session
from src.outbox.infrastructure.postgres_repository import SQLAlchemyOutboxRepository

# class RedisUnitOfWork(IUnitOfWork):
#     def __init__(self, redis_client: redis.Redis):
#         self._redis_client = redis_client

#     def __enter__(self):
#         self.session_repository = RedisSessionRepository(self._redis_client)
#         return self

#     def __exit__(self, exc_type, exc_val, exc_tb):
#         if exc_type:
#             self.rollback()
#         else:
#             self.commit()

#     def commit(self):
#         pass

#     def rollback(self):
#         pass

class SQLAlchemyUnitOfWork:
    def __init__(self, session: Session):
        self.session = session

    async def __aenter__(self):
        self.otp = SQLAlchemyOTPRepository(self.session)
        self.accounts = SQLAlchemyAccountRepository(self.session)
        self.user_profiles = SQLAlchemyUserProfileRepository(self.session)
        self.courier_profiles = SQLAlchemyCourierProfileRepository(self.session)
        self.refresh_tokens = SQLAlchemyRefreshTokenRepository(self.session)
        #outbox
        self.outbox = SQLAlchemyOutboxRepository(self.session)
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