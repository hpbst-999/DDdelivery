from src.outbox.infrastructure.models import OutboxMessageModel
from src.outbox.domain.outbox_message import OutboxMessage
from src.outbox.domain.enum import OutboxStatus
from sqlalchemy.orm import Session
from sqlalchemy import select

class SQLAlchemyOutboxRepository:
    def __init__(self, session:Session):
        self.session = session

    def _to_entity(self, model: OutboxMessageModel) -> OutboxMessage:
        return OutboxMessage(
            id= model.id,
            type=model.type,
            payload=model.payload,
            status=OutboxStatus(model.status),
            retry_count=model.retry_count,
            max_retries=model.max_retries,
            created_at=model.created_at,
            processed_at=model.processed_at
        )

    def add(self, message:OutboxMessage) -> None:
        model = OutboxMessageModel(
            id=message.id,
            type=message.type,
            payload=message.payload,
            status=message.status,
            retry_count=message.retry_count,
            max_retries=message.max_retries,
            created_at=message.created_at,
            processed_at=message.processed_at,
        )
        self.session.add(model)

    def update(self, message: OutboxMessage) -> None:
        stmt = select(OutboxMessage).where(OutboxMessageModel.id == message.ig)
        model = self.session.scalars(stmt).one_or_none()
        if model:
            model.status = message.status
            model.retry_count = message.retry_count
            model.processed_at = message.processed_at

    def get_pending_batch(self, limit: int = 10) -> list[OutboxMessage]:
        stmt = select(OutboxMessageModel).where(OutboxMessageModel.status == OutboxStatus.PENDING).order_by(OutboxMessageModel.created_at.asc()).limit(limit).with_for_update(skip_locked=True)
        models = self.session.scalars(stmt).all()
    
        return [self._to_entity(m) for m in models]