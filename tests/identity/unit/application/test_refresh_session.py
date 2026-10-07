import uuid
from datetime import UTC, datetime, timedelta

import pytest
import pytest_asyncio

from src.identity.application.dtos.token_pair import TokenPair
from src.identity.application.use_cases.refresh_session import RefreshSessionUseCase
from src.identity.domain.entities.refresh_token import RefreshToken
from src.identity.domain.exceptions import DomainException, SessionNotFoundError
from tests.identity.fakes.fake_uow import FakeUnitOfWork


class FakeTokenServiceWithValidation:
    def __init__(self):
        self.invalid_tokens = set()

    def validate_refresh_token(self, token: str) -> None:
        if token in self.invalid_tokens:
            raise ValueError("Invalid token signature")

    def generate_pair(self, account_id: uuid.UUID) -> TokenPair:
        return TokenPair(
            access_token=f"new_access_for_{account_id}",
            refresh_token=f"new_refresh_for_{account_id}",
        )


@pytest_asyncio.fixture
async def uow():
    return FakeUnitOfWork()


@pytest.fixture
def token_service():
    return FakeTokenServiceWithValidation()


@pytest.fixture
def use_case(uow, token_service):
    return RefreshSessionUseCase(uow=uow, token_service=token_service)


@pytest.mark.asyncio
async def test_refresh_session_success(use_case, uow, token_service):

    token_id = uuid.uuid4()
    account_id = uuid.uuid4()
    old_token = "valid_old_refresh_token"

    await uow.refresh_tokens.save_refresh_token(
        RefreshToken(
            id=token_id,
            account_id=account_id,
            refresh_token=old_token,
            expires_at=datetime.now(UTC) + timedelta(days=10),
            created_at=datetime.now(UTC),
        )
    )

    new_tokens = await use_case.execute(raw_refresh_token=old_token)

    assert new_tokens.access_token
    assert new_tokens.refresh_token == "new_refresh_for_" + str(account_id)

    assert len(uow.refresh_tokens.tokens) == 2
    assert uow.refresh_tokens.tokens[token_id].is_revoked is True

    new_saved_token = await uow.refresh_tokens.get_refresh_token(new_tokens.refresh_token)
    assert new_saved_token is not None
    assert new_saved_token.account_id == account_id

    assert uow.committed is True


@pytest.mark.asyncio
async def test_refresh_session_invalid_token_format(use_case, token_service):

    bad_token = "malformed_token"
    token_service.invalid_tokens.add(bad_token)

    with pytest.raises(DomainException, match="Invalid token signature"):
        await use_case.execute(raw_refresh_token=bad_token)


@pytest.mark.asyncio
async def test_refresh_session_not_found_in_db(use_case):

    with pytest.raises(SessionNotFoundError, match="Session not found"):
        await use_case.execute(raw_refresh_token="crypto_valid_but_ghost_token")


@pytest.mark.asyncio
async def test_refresh_session_expired(use_case, uow):

    token_id = uuid.uuid4()
    expired_token = "expired_refresh_token"

    past_time = datetime.now(UTC) - timedelta(days=1)
    await uow.refresh_tokens.save_refresh_token(
        RefreshToken(
            id=token_id,
            account_id=uuid.uuid4(),
            refresh_token=expired_token,
            expires_at=past_time,
            created_at=past_time - timedelta(days=30),
        )
    )

    with pytest.raises(DomainException, match="Refresh token has expired"):
        await use_case.execute(raw_refresh_token=expired_token)

    assert uow.refresh_tokens.tokens[token_id].is_revoked is True
    assert await uow.refresh_tokens.get_refresh_token(expired_token) is None
    assert uow.committed is True
