from typing import Any, Protocol
from src.outbox.domain.outbox_message import OutboxMessage

class IOutboxRepository(Protocol):
    def add(self, message: OutboxMessage) -> None:
        ...

    def update(self, message: OutboxMessage) -> None:
        ...

    def get_pending_batch(self, limit: int = 10) -> list[OutboxMessage]:
        ...

class IMessagePublisher(Protocol):
    def publish(self, type: str, payload: dict[str, Any])-> None:
        ...

class IOutboxUnitOfWork(Protocol):
    outbox: IOutboxRepository

    def __enter__(self):
        ...

    def __exit__(self, exc_type, exc_val, exc_tb):
        ...

    def commit(self):
        ...

    def rollback(self):
        ...