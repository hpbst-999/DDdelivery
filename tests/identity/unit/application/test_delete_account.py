import uuid

import pytest
import pytest_asyncio

from src.identity.application.use_cases.delete_account import DeleteAccountUseCase
from src.identity.domain.entities.account import Account
from src.identity.domain.entities.user_profile import UserProfile
from src.identity.domain.exceptions import AccountNotFoundError
from src.identity.domain.value_objects.phone_number import PhoneNumber
from tests.identity.fakes.fake_uow import FakeUnitOfWork


@pytest_asyncio.fixture
async def uow():
    return FakeUnitOfWork()


@pytest.fixture
def use_case(uow):
    return DeleteAccountUseCase(uow=uow)


@pytest.fixture
def existing_account_and_profile():
    account_id = uuid.uuid4()
    account = Account(id=account_id, phone_number=PhoneNumber("+79991234567"))
    profile = UserProfile(id=uuid.uuid4(), account_id=account_id, name="Test")
    return account, profile


@pytest.mark.asyncio
async def test_delete_account_success_cascades_to_profile(
    use_case, uow, existing_account_and_profile
):
    account, profile = existing_account_and_profile

    await uow.accounts.add_account(account)
    await uow.user_profiles.add_user(profile)

    assert len(uow.accounts.accounts) == 1
    assert len(uow.user_profiles.profiles) == 1

    await use_case.execute(account_id=account.id)

    assert uow.committed is True

    assert await uow.accounts.get_account_by_id(account.id) is None

    assert len(uow.user_profiles.profiles) == 0


@pytest.mark.asyncio
async def test_delete_account_not_found(use_case, uow):
    fake_id = uuid.uuid4()

    with pytest.raises(AccountNotFoundError, match="Account not found"):
        await use_case.execute(account_id=fake_id)

    assert uow.committed is False
