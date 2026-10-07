import uuid
from datetime import UTC, datetime

from src.courier.domain.exceptions import InvalidCourierStatusTransitionError
from src.courier.domain.value_objects.enums import CourierStatus


class CourierProfile:
    def __init__(
        self,
        id: uuid.UUID,
        account_id: uuid.UUID,
        full_name: str | None = None,
        inn: str | None = None,
        is_verified: bool = False,
        verified_at: datetime | None = None,
        status: CourierStatus = CourierStatus.OFFLINE,
    ):
        self.id = id
        self.account_id = account_id
        self.full_name = full_name
        self.inn = inn
        self.is_verified = is_verified
        self.verified_at = verified_at
        self.status = status

    def verify(self) -> None:
        self.is_verified = True
        self.verified_at = datetime.now(UTC)

    def revoke_verification(self) -> None:
        self.is_verified = False
        self.verified_at = None
        self.go_offline()

    def go_online(self) -> None:
        if not self.is_verified:
            raise ValueError("Not verified")
        self.status = CourierStatus.ONLINE

    def go_offline(self) -> None:
        if self.status == CourierStatus.BUSY:
            raise InvalidCourierStatusTransitionError(
                "You cannot complete the shift while you have an active order"
            )
        self.status = CourierStatus.OFFLINE

    def assign_order(self) -> None:
        if self.status != CourierStatus.ONLINE:
            raise InvalidCourierStatusTransitionError("Not online")
        self.status = CourierStatus.BUSY

    def complete_order(self) -> None:
        if self.status != CourierStatus.BUSY:
            raise InvalidCourierStatusTransitionError(
                "Cannot complete order when courier is not busy"
            )
        self.status = CourierStatus.ONLINE

    def change_status(self, target_status: CourierStatus) -> None:
        if self.status == target_status:
            return

        if target_status == CourierStatus.BUSY:
            raise InvalidCourierStatusTransitionError("The BUSY status is set by the system")

        if target_status == CourierStatus.ONLINE:
            self.go_online()
        elif target_status == CourierStatus.OFFLINE:
            self.go_offline()
