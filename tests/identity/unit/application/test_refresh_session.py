import uuid
import pytest
from unittest.mock import MagicMock
from datetime import UTC, datetime, timedelta

from src.identity.application.interfaces import ITokenData, ITokenGenerator, ITokenValidator
from src.identity.application.use_cases.refresh_session import RefreshSessionUseCase
from src.identity.domain.entities.refresh_token import RefreshToken
from src.identity.domain.exceptions import (
    InvalidTokenError,
    SessionNotFoundError,
    TokenExpiredError,
)
from tests.identity.fakes.fake_uow import FakeUnitOfWork


@pytest.fixture
def mock_token_data() -> ITokenData:
    token_data = MagicMock(spec=ITokenData)
    token_data.access_token = "new_access_token"
    token_data.refresh_token = "new_refresh_token"
    return token_data


@pytest.fixture
def mock_token_generator(mock_token_data: ITokenData) -> MagicMock:
    generator = MagicMock(spec=ITokenGenerator)
    generator.generate_pair.return_value = mock_token_data
    return generator


@pytest.fixture
def mock_token_validator() -> MagicMock:
    validator = MagicMock(spec=ITokenValidator)
    return validator


@pytest.fixture
def active_refresh_token() -> RefreshToken:
    now = datetime.now(UTC)
    token = RefreshToken(
        id=uuid.uuid4(),
        account_id=uuid.uuid4(),
        refresh_token="valid_raw_token",
        expires_at=now + timedelta(days=30),
        is_revoked=False,
        created_at=now,
    )
    return token


@pytest.mark.asyncio
async def test_refresh_session_invalid_token_format_raises_error(
    mock_token_generator: MagicMock,
    mock_token_validator: MagicMock,
) -> None:
    uow = FakeUnitOfWork()
    mock_token_validator.validate_refresh_token.side_effect = ValueError("Malformed token")
    
    use_case = RefreshSessionUseCase(
        uow=uow,
        token_generator=mock_token_generator,
        token_validator=mock_token_validator,
    )

    with pytest.raises(InvalidTokenError):
        await use_case.execute(raw_refresh_token="invalid_token")


@pytest.mark.asyncio
async def test_refresh_session_not_found_raises_error(
    mock_token_generator: MagicMock,
    mock_token_validator: MagicMock,
) -> None:
    uow = FakeUnitOfWork()
    
    use_case = RefreshSessionUseCase(
        uow=uow,
        token_generator=mock_token_generator,
        token_validator=mock_token_validator,
    )

    with pytest.raises(SessionNotFoundError, match="Session not found"):
        await use_case.execute(raw_refresh_token="valid_token")


@pytest.mark.asyncio
async def test_refresh_session_expired_token_revokes_and_raises_error(
    mock_token_generator: MagicMock,
    mock_token_validator: MagicMock,
) -> None:
    uow = FakeUnitOfWork()
    now = datetime.now(UTC)

    expired_token = RefreshToken(
        id=uuid.uuid4(),
        account_id=uuid.uuid4(),
        refresh_token="expired_raw_token",
        expires_at=now - timedelta(days=1),
        created_at=now - timedelta(days=31),
    )
    await uow.refresh_tokens.save_refresh_token(expired_token)

    use_case = RefreshSessionUseCase(
        uow=uow,
        token_generator=mock_token_generator,
        token_validator=mock_token_validator,
    )

    with pytest.raises(TokenExpiredError, match="Refresh token has expired"):
        await use_case.execute(raw_refresh_token="expired_raw_token")

    assert uow.committed is True
    assert expired_token.is_revoked is True


@pytest.mark.asyncio
async def test_refresh_session_success(
    mock_token_generator: MagicMock,
    mock_token_validator: MagicMock,
    mock_token_data: ITokenData,
    active_refresh_token: RefreshToken,
) -> None:
    uow = FakeUnitOfWork()
    await uow.refresh_tokens.save_refresh_token(active_refresh_token)

    use_case = RefreshSessionUseCase(
        uow=uow,
        token_generator=mock_token_generator,
        token_validator=mock_token_validator,
    )

    result = await use_case.execute(raw_refresh_token=active_refresh_token.refresh_token)

    assert result == mock_token_data
    assert uow.committed is True

    assert active_refresh_token.is_revoked is True

    assert len(uow.refresh_tokens.tokens) == 2