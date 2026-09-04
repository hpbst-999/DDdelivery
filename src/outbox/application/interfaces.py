from typing import Any, Protocol, Self
from src.outbox.domain.outbox_message import OutboxMessage

class IOutboxRepository(Protocol):
    async def add(self, message: OutboxMessage) -> None:
        ...

    async def update(self, message: OutboxMessage) -> None:
        ...

    async def get_pending_batch(self, limit: int = 10) -> list[OutboxMessage]:
        ...

class IMessagePublisher(Protocol):
    async def publish(self, type: str, payload: dict[str, Any])-> None:
        ...

class IOutboxUnitOfWork(Protocol):
    outbox: IOutboxRepository

    async def __aenter__(self) -> Self:
        ...

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        ...

    async def commit(self) -> None:
        ...

    async def rollback(self) -> None:
        ...