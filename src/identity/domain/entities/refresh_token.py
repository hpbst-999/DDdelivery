import uuid
from datetime import UTC, datetime


class RefreshToken:
    def __init__(
        self,
        id: uuid.UUID,
        account_id: uuid.UUID,
        refresh_token: str,
        expires_at: datetime,
        is_revoked: bool = False,
        created_at: datetime | None = None,
    ) -> None:
        self.id = id
        self.account_id = account_id
        self.refresh_token = refresh_token
        self.expires_at = expires_at
        self.is_revoked = is_revoked
        self.created_at = created_at if created_at is not None else datetime.now(UTC)

    def revoke(self) -> None:
        self.is_revoked = True

    @property
    def is_valid(self) -> bool:
        return not self.is_revoked and datetime.now(UTC) < self.expires_at
