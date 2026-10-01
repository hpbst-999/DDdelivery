import uuid

import pytest
import pytest_asyncio

from src.identity.application.dtos.oauth_user import OAuthUser
from src.identity.application.use_cases.login_oauth import LoginWithOAuthUseCase
from src.identity.domain.entities.account import Account
from src.identity.domain.value_objects.email import Email
from tests.identity.fakes.fake_uow import FakeUnitOfWork


class FakeTokenService:
    def generate_pair(self, account_id: str) -> dict:
        return {
            "access_token": f"oauth_access_for_{account_id}",
            "refresh_token": f"oauth_refresh_for_{account_id}",
        }


@pytest_asyncio.fixture
async def uow():
    return FakeUnitOfWork()


@pytest.fixture
def token_service():
    return FakeTokenService()


@pytest.fixture
def use_case(uow, token_service):
    return LoginWithOAuthUseCase(uow=uow, token_service=token_service)


@pytest.mark.asyncio
async def test_oauth_login_new_user_creates_account_and_profile(use_case, uow):

    oauth_data = OAuthUser(email="new_user@example.com", name="Alex Smith")

    tokens = await use_case.execute(user_info=oauth_data)

    assert "access_token" in tokens
    assert "refresh_token" in tokens

    assert len(uow.accounts.accounts) == 1
    assert len(uow.user_profiles.profiles) == 1

    saved_account = list(uow.accounts.accounts.values())[0]
    assert str(saved_account.email) == "new_user@example.com"

    saved_profile = list(uow.user_profiles.profiles.values())[0]
    assert saved_profile.name == "Alex Smith"

    assert uow.committed is True


@pytest.mark.asyncio
async def test_oauth_login_existing_user_skips_creation(use_case, uow):

    email_str = "existing_user@example.com"
    existing_account = Account(id=uuid.uuid4(), email=Email(email_str))
    await uow.accounts.add_account(existing_account)

    oauth_data = OAuthUser(email=email_str, name="Should Not Be Updated Here")

    tokens = await use_case.execute(user_info=oauth_data)

    assert "access_token" in tokens
    assert len(uow.accounts.accounts) == 1
    assert len(uow.user_profiles.profiles) == 0
    assert uow.committed is True
