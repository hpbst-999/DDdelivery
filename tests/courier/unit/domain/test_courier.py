import uuid
from datetime import UTC

import pytest

from src.courier.domain.entities.courier_profile import CourierProfile
from src.courier.domain.exceptions import InvalidCourierStatusTransitionError
from src.courier.domain.value_objects.enums import CourierStatus


@pytest.fixture
def unverified_courier() -> CourierProfile:
    return CourierProfile(
        id=uuid.uuid4(),
        account_id=uuid.uuid4(),
        full_name="Иван Иванович",
    )


@pytest.fixture
def verified_courier() -> CourierProfile:
    courier = CourierProfile(
        id=uuid.uuid4(),
        account_id=uuid.uuid4(),
    )
    courier.verify()
    return courier


def test_courier_initialization(unverified_courier: CourierProfile) -> None:
    assert unverified_courier.status == CourierStatus.OFFLINE
    assert unverified_courier.is_verified is False
    assert unverified_courier.verified_at is None


def test_verify_courier(unverified_courier: CourierProfile) -> None:
    unverified_courier.verify()

    assert unverified_courier.is_verified is True
    assert unverified_courier.verified_at is not None
    assert unverified_courier.verified_at.tzinfo == UTC


def test_revoke_verification(verified_courier: CourierProfile) -> None:
    verified_courier.revoke_verification()

    assert verified_courier.is_verified is False
    assert verified_courier.verified_at is None
    assert verified_courier.status == CourierStatus.OFFLINE


def test_go_online_success(verified_courier: CourierProfile) -> None:
    verified_courier.go_online()
    assert verified_courier.status == CourierStatus.ONLINE


def test_go_online_fails_if_not_verified(unverified_courier: CourierProfile) -> None:
    with pytest.raises(ValueError, match="Not verified"):
        unverified_courier.go_online()


def test_go_offline_success(verified_courier: CourierProfile) -> None:
    verified_courier.go_online()
    verified_courier.go_offline()

    assert verified_courier.status == CourierStatus.OFFLINE


def test_go_offline_fails_if_busy(verified_courier: CourierProfile) -> None:
    verified_courier.go_online()
    verified_courier.assign_order()

    with pytest.raises(InvalidCourierStatusTransitionError, match="cannot complete the shift"):
        verified_courier.go_offline()


def test_assign_order_success(verified_courier: CourierProfile) -> None:
    verified_courier.go_online()
    verified_courier.assign_order()

    assert verified_courier.status == CourierStatus.BUSY


def test_assign_order_fails_if_not_online(verified_courier: CourierProfile) -> None:
    with pytest.raises(InvalidCourierStatusTransitionError, match="Not online"):
        verified_courier.assign_order()


def test_complete_order_success(verified_courier: CourierProfile) -> None:
    verified_courier.go_online()
    verified_courier.assign_order()
    verified_courier.complete_order()

    assert verified_courier.status == CourierStatus.ONLINE


def test_complete_order_fails_if_not_busy(verified_courier: CourierProfile) -> None:
    verified_courier.go_online()

    with pytest.raises(InvalidCourierStatusTransitionError, match="Cannot complete order"):
        verified_courier.complete_order()


def test_change_status_ignores_same_status(verified_courier: CourierProfile) -> None:
    verified_courier.change_status(CourierStatus.OFFLINE)
    assert verified_courier.status == CourierStatus.OFFLINE


def test_change_status_blocks_manual_busy(verified_courier: CourierProfile) -> None:
    with pytest.raises(
        InvalidCourierStatusTransitionError, match="BUSY status is set by the system"
    ):
        verified_courier.change_status(CourierStatus.BUSY)


def test_change_status_routes_correctly(verified_courier: CourierProfile) -> None:
    verified_courier.change_status(CourierStatus.ONLINE)
    assert verified_courier.status == CourierStatus.ONLINE

    verified_courier.change_status(CourierStatus.OFFLINE)
    assert verified_courier.status == CourierStatus.OFFLINE
