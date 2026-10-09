import uuid

import pytest

from src.courier.domain.entities.courier_profile import CourierProfile
from src.courier.domain.value_objects.enums import CourierStatus
from src.courier.infrastructure.uow import UnitOfWork


@pytest.fixture
def new_courier() -> CourierProfile:
    return CourierProfile(
        id=uuid.uuid4(),
        account_id=uuid.uuid4(),
        full_name="Тестовый Курьер",
        inn="123456789012",
        is_verified=True,
        verified_at=None,
        status=CourierStatus.ONLINE,
    )


@pytest.mark.asyncio
async def test_uow_commit_persists_courier(uow: UnitOfWork, new_courier: CourierProfile) -> None:
    async with uow:
        await uow.courier_profiles.add_courier(new_courier)
        await uow.commit()

    async with uow:
        retrieved = await uow.courier_profiles.get_courier_by_id(new_courier.id)
        assert retrieved is not None
        assert retrieved.id == new_courier.id
        assert retrieved.status == CourierStatus.ONLINE


@pytest.mark.asyncio
async def test_uow_rollback_on_exception(uow: UnitOfWork, new_courier: CourierProfile) -> None:
    with pytest.raises(RuntimeError):
        async with uow:
            await uow.courier_profiles.add_courier(new_courier)
            raise RuntimeError("Database transaction failure simulation")

    async with uow:
        retrieved = await uow.courier_profiles.get_courier_by_id(new_courier.id)
        assert retrieved is None