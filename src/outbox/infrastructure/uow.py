from sqlalchemy.orm import Session
from src.outbox.infrastructure.postgres_repository import SQLAlchemyOutboxRepository

class SQLAlchemyUnitOfWork:
    def __init__(self, session: Session):
        self.session = session
        self.outbox = SQLAlchemyOutboxRepository(self.session)

    def __enter__(self):
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