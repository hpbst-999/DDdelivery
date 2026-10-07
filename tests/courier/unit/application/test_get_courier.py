import uuid

import pytest
import pytest_asyncio

from src.courier.application.use_cases.get_courier_profile import GetCourierProfileUseCase
from src.courier.domain.entities.courier_profile import CourierProfile
from src.courier.domain.exceptions import ProfileNotFoundError
from tests.courier.fakes.fake_uow import FakeUnitOfWork


@pytest_asyncio.fixture
async def uow():
    return FakeUnitOfWork()


@pytest.fixture
def use_case(uow):
    return GetCourierProfileUseCase(uow=uow)


@pytest.fixture
def account_id():
    return uuid.uuid4()


@pytest.mark.asyncio
async def test_execute_success_returns_profile(use_case, uow, account_id):

    profile = CourierProfile(id=uuid.uuid4(), account_id=account_id)
    await uow.courier_profiles.add_courier(profile)

    result = await use_case.execute(account_id=account_id)

    assert result.account_id == account_id
    assert result.id == profile.id
    assert uow.committed is False
    assert uow.rolled_back is False


@pytest.mark.asyncio
async def test_execute_raises_not_found(use_case, uow, account_id):

    with pytest.raises(ProfileNotFoundError):
        await use_case.execute(account_id=account_id)

    assert uow.committed is False
    assert uow.rolled_back is True
