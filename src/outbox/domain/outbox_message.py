import uuid
from typing import Any
from datetime import datetime, timezone
from src.outbox.domain.enum import OutboxStatus

class OutboxMessage:
    def __init__(self, 
            id:uuid.UUID, 
            type: str,
            payload: dict[str, Any], 
            status: OutboxStatus = OutboxStatus.PENDING, 
            retry_count: int = 0,
            max_retries: int = 5,
            created_at: datetime | None = None,
            processed_at: datetime | None = None):
        self.id = id
        self.type = type
        self.payload = payload
        self.status = status
        self.retry_count = retry_count
        self.max_retries = max_retries
        self.created_at =  created_at if created_at is not None else datetime.now(timezone.utc)
        self.processed_at = processed_at

    def event_as_processed(self, processed_at:datetime| None = None) -> None:
        self.status = OutboxStatus.PROCESSED
        self.processed_at = processed_at or datetime.now(timezone.utc)

    def event_failed(self) -> None:
        self.retry_count +=1
        if self.retry_count >= self.max_retries:
            self.status = OutboxStatus.FAILED

    def is_pending(self) -> bool:
        return self.status == OutboxStatus.PENDING

    def can_retry(self) -> bool:
        return self.status == OutboxStatus.PENDING and self.retry_count < self.max_retries
