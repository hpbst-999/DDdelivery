from unittest.mock import AsyncMock, MagicMock

import pytest

from src.identity.application.interfaces import (
    ICacheRepository,
    IOAuthServiceFactory,
    IUnitOfWork,
)
from src.identity.application.use_cases.login_oauth import LoginWithOAuthUseCase
from src.identity.domain.exceptions import (
    InvalidOAuthStateError,
    OAuthStateMismatchError,
)
from src.identity.domain.value_objects.email import Email


@pytest.fixture
def mock_uow() -> MagicMock:
    uow = MagicMock(spec=IUnitOfWork)
    uow.__aenter__ = AsyncMock(return_value=uow)
    uow.__aexit__ = AsyncMock(return_value=None)
    uow.commit = AsyncMock()
    return uow


@pytest.fixture
def mock_cache() -> MagicMock:
    cache = MagicMock(spec=ICacheRepository)
    cache.get = AsyncMock()
    cache.delete = AsyncMock()
    return cache


@pytest.fixture
def mock_oauth_service() -> MagicMock:
    service = MagicMock()
    service.get_user_info = AsyncMock()
    return service


@pytest.fixture
def mock_factory(mock_oauth_service: MagicMock) -> MagicMock:
    factory = MagicMock(spec=IOAuthServiceFactory)
    factory.get_service = MagicMock(return_value=mock_oauth_service)
    return factory


@pytest.mark.asyncio
async def test_login_with_oauth_success(
    mock_uow: MagicMock,
    mock_factory: MagicMock,
    mock_oauth_service: MagicMock,
    mock_cache: MagicMock,
) -> None:
    state = "test_state_123"
    provider = "google"
    code = "oauth_auth_code_xyz"
    user_email_str = "user@gmail.com"

    mock_cache.get.return_value = provider
    mock_user_info = MagicMock()
    mock_user_info.email = user_email_str
    mock_oauth_service.get_user_info.return_value = mock_user_info

    use_case = LoginWithOAuthUseCase(
        uow=mock_uow,
        factory=mock_factory,
        cache=mock_cache,
    )

    result = await use_case.execute(state=state, provider=provider, code=code)

    assert isinstance(result, Email)
    assert result == Email(user_email_str)

    cache_key = f"state:{state}"
    mock_cache.get.assert_awaited_once_with(key=cache_key)
    mock_cache.delete.assert_awaited_once_with(key=cache_key)
    mock_factory.get_service.assert_called_once_with(provider)
    mock_oauth_service.get_user_info.assert_awaited_once_with(code=code)


@pytest.mark.asyncio
async def test_login_with_oauth_invalid_or_expired_state(
    mock_uow: MagicMock,
    mock_factory: MagicMock,
    mock_cache: MagicMock,
) -> None:
    state = "expired_state_999"
    mock_cache.get.return_value = None

    use_case = LoginWithOAuthUseCase(
        uow=mock_uow,
        factory=mock_factory,
        cache=mock_cache,
    )

    with pytest.raises(InvalidOAuthStateError, match="State is invalid or expired"):
        await use_case.execute(state=state, provider="google", code="dummy_code")

    mock_cache.get.assert_awaited_once_with(key=f"state:{state}")
    mock_cache.delete.assert_not_awaited()
    mock_factory.get_service.assert_not_called()


@pytest.mark.asyncio
async def test_login_with_oauth_provider_mismatch(
    mock_uow: MagicMock,
    mock_factory: MagicMock,
    mock_cache: MagicMock,
) -> None:
    state = "state_google_flow"
    mock_cache.get.return_value = "google"

    use_case = LoginWithOAuthUseCase(
        uow=mock_uow,
        factory=mock_factory,
        cache=mock_cache,
    )

    with pytest.raises(OAuthStateMismatchError, match="State provider mismatch"):
        await use_case.execute(state=state, provider="yandex", code="dummy_code")

    cache_key = f"state:{state}"
    mock_cache.get.assert_awaited_once_with(key=cache_key)
    mock_cache.delete.assert_awaited_once_with(key=cache_key)
    mock_factory.get_service.assert_not_called()