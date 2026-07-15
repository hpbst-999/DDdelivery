import redis
from src.identity.application.interfaces import IUnitOfWork
from src.identity.infrastructure.redis_repositories import RedisSessionRepository, RedisOTPRepository
from src.identity.infrastructure.postgres_repositories import (
    SQLAlchemyAccountRepository,
    SQLAlchemyUserProfileRepository,
    SQLAlchemyCourierProfileRepository
)
from sqlalchemy.orm import Session

class RedisUnitOfWork(IUnitOfWork):
    def __init__(self, redis_client: redis.Redis):
        self._redis_client = redis_client

    def __enter__(self):
        self.session_repository = RedisSessionRepository(self._redis_client)
        self.otp_repository = RedisOTPRepository(self._redis_client)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self.rollback()
        else:
            self.commit()

    def commit(self):
        pass

    def rollback(self):
        pass

class SQLAlchemyUnitOfWork(IUnitOfWork):
    def __init__(self, session: Session):
        self.session = session

    def __enter__(self):
        self.accounts = SQLAlchemyAccountRepository(self.session)
        self.user_profiles = SQLAlchemyUserProfileRepository(self.session)
        self.courier_profiles = SQLAlchemyCourierProfileRepository(self.session)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self.rollback()
        else:
            self.commit()

    def commit(self):
        self.session.commit()

    def rollback(self):
        self.session.rollback()