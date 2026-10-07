import uuid

import pytest
import pytest_asyncio

from src.courier.application.use_cases.delete_courier import DeleteCourierUseCase
from src.courier.domain.entities.courier_profile import CourierProfile
from src.courier.domain.exceptions import ProfileNotFoundError
from tests.courier.fakes.fake_uow import FakeUnitOfWork


@pytest_asyncio.fixture
async def uow():
    return FakeUnitOfWork()


@pytest.fixture
def use_case(uow):
    return DeleteCourierUseCase(uow=uow)


@pytest.fixture
def account_id():
    return uuid.uuid4()


@pytest.fixture
def existing_profile(account_id):
    return CourierProfile(id=uuid.uuid4(), account_id=account_id)


@pytest.mark.asyncio
async def test_execute_success_deletes_profile_and_commits(
    use_case, uow, account_id, existing_profile
):
    await uow.courier_profiles.add_courier(existing_profile)

    await use_case.execute(account_id=account_id)

    deleted_profile = await uow.courier_profiles.get_courier_by_account_id(account_id)

    assert deleted_profile is None
    assert len(uow.courier_profiles._data) == 0
    assert uow.committed is True
    assert uow.rolled_back is False


@pytest.mark.asyncio
async def test_execute_raises_not_found(use_case, uow, account_id):
    with pytest.raises(ProfileNotFoundError):
        await use_case.execute(account_id=account_id)

    assert uow.committed is False
    assert uow.rolled_back is True
