import uuid

import pytest
import pytest_asyncio

from src.courier.application.use_cases.change_status import ChangeCourierStatusUseCase
from src.courier.domain.entities.courier_profile import CourierProfile
from src.courier.domain.exceptions import ProfileNotFoundError
from src.courier.domain.value_objects.enums import CourierStatus
from tests.courier.fakes.fake_uow import FakeUnitOfWork


@pytest_asyncio.fixture
async def uow():
    return FakeUnitOfWork()


@pytest.fixture
def use_case(uow):
    return ChangeCourierStatusUseCase(uow=uow)


@pytest.fixture
def account_id():
    return uuid.uuid4()


@pytest.fixture
def verified_profile(account_id):
    profile = CourierProfile(id=account_id, account_id=account_id)
    profile.verify()
    return profile


@pytest.mark.asyncio
async def test_execute_success_changes_status_and_commits(
    use_case, uow, verified_profile, account_id
):
    await uow.courier_profiles.add_courier(verified_profile)
    target_status = CourierStatus.ONLINE

    await use_case.execute(account_id=account_id, target_status=target_status)

    saved_profile = await uow.courier_profiles.get_courier_by_id(account_id)
    assert saved_profile.status == CourierStatus.ONLINE
    assert uow.committed is True
    assert uow.rolled_back is False


@pytest.mark.asyncio
async def test_execute_raises_not_found_and_rolls_back(use_case, uow, account_id):
    with pytest.raises(ProfileNotFoundError, match="Coureir profile not found"):
        await use_case.execute(account_id=account_id, target_status=CourierStatus.ONLINE)

    assert uow.committed is False
    assert uow.rolled_back is True


@pytest.mark.asyncio
async def test_execute_propagates_domain_error_and_rolls_back(use_case, uow, account_id):
    unverified_profile = CourierProfile(id=account_id, account_id=account_id)
    await uow.courier_profiles.add_courier(unverified_profile)

    with pytest.raises(ValueError, match="Not verified"):
        await use_case.execute(account_id=account_id, target_status=CourierStatus.ONLINE)

    assert uow.committed is False
    assert uow.rolled_back is True
