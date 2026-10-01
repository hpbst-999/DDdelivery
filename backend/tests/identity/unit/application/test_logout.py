import uuid
from datetime import UTC, datetime, timedelta

import pytest
import pytest_asyncio

from src.identity.application.use_cases.logout import LogoutUseCase
from tests.identity.fakes.fake_uow import FakeUnitOfWork


@pytest_asyncio.fixture
async def uow():
    return FakeUnitOfWork()


@pytest.fixture
def use_case(uow):
    return LogoutUseCase(uow=uow)


@pytest.mark.asyncio
async def test_logout_success_revokes_token(use_case, uow):
    token_id = uuid.uuid4()
    refresh_token_str = "some_valid_refresh_token_string"

    await uow.refresh_tokens.save_refresh_token(
        id=token_id,
        account_id=uuid.uuid4(),
        refresh_token=refresh_token_str,
        expires_at=datetime.now(UTC) + timedelta(days=30),
        created_at=datetime.now(UTC),
    )

    assert len(uow.refresh_tokens.tokens) == 1

    await use_case.execute(refresh_token=refresh_token_str)

    assert uow.committed is True

    assert len(uow.refresh_tokens.tokens) == 0


@pytest.mark.asyncio
async def test_logout_non_existent_token_is_safe(use_case, uow):
    await use_case.execute(refresh_token="ghost_token")

    assert uow.committed is True
