import uuid
from datetime import UTC, datetime

import pytest

from src.courier.domain.entities.courier_profile import CourierProfile
from src.courier.domain.value_objects.enums import CourierStatus
from src.courier.infrastructure.postgres_repositories import SQLAlchemyCourierProfileRepository


@pytest.fixture
def sample_courier_profile() -> CourierProfile:
    return CourierProfile(
        id=uuid.uuid4(),
        account_id=uuid.uuid4(),
        full_name="Иван Иванов",
        inn="770123456789",
        is_verified=False,
        verified_at=None,
        status=CourierStatus.OFFLINE,
    )


@pytest.mark.asyncio
async def test_add_and_get_courier_by_id_success(
    courier_repo: SQLAlchemyCourierProfileRepository,
    sample_courier_profile: CourierProfile,
) -> None:
    await courier_repo.add_courier(sample_courier_profile)

    retrieved = await courier_repo.get_courier_by_id(sample_courier_profile.id)

    assert retrieved is not None
    assert retrieved.id == sample_courier_profile.id
    assert retrieved.account_id == sample_courier_profile.account_id
    assert retrieved.full_name == "Иван Иванов"
    assert retrieved.inn == "770123456789"
    assert retrieved.is_verified is False
    assert retrieved.verified_at is None
    assert retrieved.status == CourierStatus.OFFLINE
    assert isinstance(retrieved.status, CourierStatus)


@pytest.mark.asyncio
async def test_get_courier_by_account_id_success(
    courier_repo: SQLAlchemyCourierProfileRepository,
    sample_courier_profile: CourierProfile,
) -> None:
    await courier_repo.add_courier(sample_courier_profile)

    retrieved = await courier_repo.get_courier_by_account_id(sample_courier_profile.account_id)

    assert retrieved is not None
    assert retrieved.id == sample_courier_profile.id
    assert retrieved.account_id == sample_courier_profile.account_id


@pytest.mark.asyncio
async def test_get_non_existent_courier_returns_none(
    courier_repo: SQLAlchemyCourierProfileRepository,
) -> None:
    result_by_id = await courier_repo.get_courier_by_id(uuid.uuid4())
    result_by_account = await courier_repo.get_courier_by_account_id(uuid.uuid4())

    assert result_by_id is None
    assert result_by_account is None


@pytest.mark.asyncio
async def test_update_courier_success(
    courier_repo: SQLAlchemyCourierProfileRepository,
    sample_courier_profile: CourierProfile,
) -> None:
    await courier_repo.add_courier(sample_courier_profile)

    sample_courier_profile.full_name = "Иван Петров"
    sample_courier_profile.inn = "779988776655"
    sample_courier_profile.status = CourierStatus.ONLINE

    await courier_repo.update_courier(sample_courier_profile)

    updated = await courier_repo.get_courier_by_id(sample_courier_profile.id)
    assert updated is not None
    assert updated.full_name == "Иван Петров"
    assert updated.inn == "779988776655"
    assert updated.status == CourierStatus.ONLINE


@pytest.mark.asyncio
async def test_delete_courier_by_account_id_success(
    courier_repo: SQLAlchemyCourierProfileRepository,
    sample_courier_profile: CourierProfile,
) -> None:
    await courier_repo.add_courier(sample_courier_profile)

    await courier_repo.delete_courier(sample_courier_profile.account_id)

    deleted = await courier_repo.get_courier_by_id(sample_courier_profile.id)
    assert deleted is None