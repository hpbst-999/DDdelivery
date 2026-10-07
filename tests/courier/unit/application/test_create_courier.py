import uuid

import pytest
import pytest_asyncio

from src.courier.application.use_cases.create_courier import CreateCourierUseCase
from src.courier.domain.entities.courier_profile import CourierProfile
from src.courier.domain.exceptions import ProfileAlreadyExistsError
from tests.courier.fakes.fake_uow import FakeUnitOfWork


@pytest_asyncio.fixture
async def uow():
    return FakeUnitOfWork()


@pytest.fixture
def use_case(uow):
    return CreateCourierUseCase(uow=uow)


@pytest.fixture
def account_id():
    return uuid.uuid4()


@pytest.mark.asyncio
async def test_execute_creates_profile_when_not_exists(use_case, uow, account_id):

    await use_case.execute(account_id=account_id)

    saved_profile = await uow.courier_profiles.get_courier_by_account_id(account_id)

    assert saved_profile is not None
    assert saved_profile.account_id == account_id
    assert saved_profile.id is not None
    assert uow.committed is True
    assert uow.rolled_back is False


@pytest.mark.asyncio
async def test_execute_raises_error_if_profile_already_exists(use_case, uow, account_id):
    existing_profile = CourierProfile(id=uuid.uuid4(), account_id=account_id)
    await uow.courier_profiles.add_courier(existing_profile)

    with pytest.raises(ProfileAlreadyExistsError):
        await use_case.execute(account_id=account_id)

    assert uow.committed is False
    assert uow.rolled_back is True
