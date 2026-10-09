from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.identity.application.interfaces import ICacheRepository, IOAuthServiceFactory
from src.identity.application.use_cases.get_oauth_url import GetOAuthUrlUseCase
from src.identity.domain.exceptions import OAuthProviderNotSupportedError


@pytest.fixture
def mock_cache() -> MagicMock:
    cache = MagicMock(spec=ICacheRepository)
    cache.set = AsyncMock()
    return cache


@pytest.fixture
def mock_oauth_service() -> MagicMock:
    service = MagicMock()
    service.get_authorization_url = MagicMock(
        return_value="https://accounts.google.com/o/oauth2/v2/auth?state=fixed_test_state"
    )
    return service


@pytest.fixture
def mock_factory(mock_oauth_service: MagicMock) -> MagicMock:
    factory = MagicMock(spec=IOAuthServiceFactory)
    factory.get_service = MagicMock(return_value=mock_oauth_service)
    return factory


@pytest.mark.asyncio
async def test_get_oauth_url_success(
    mock_factory: MagicMock,
    mock_oauth_service: MagicMock,
    mock_cache: MagicMock,
) -> None:
    provider = "google"
    fixed_state = "fixed_test_state"
    expected_url = f"https://accounts.google.com/o/oauth2/v2/auth?state={fixed_state}"
    mock_oauth_service.get_authorization_url.return_value = expected_url

    use_case = GetOAuthUrlUseCase(factory=mock_factory, cache=mock_cache)

    with patch("secrets.token_urlsafe", return_value=fixed_state):
        result = await use_case.execute(provider=provider)

    assert result == expected_url
    mock_factory.get_service.assert_called_once_with(provider)
    mock_cache.set.assert_awaited_once_with(
        key=f"state:{fixed_state}",
        value=provider,
        ttl_second=600,
    )
    mock_oauth_service.get_authorization_url.assert_called_once_with(fixed_state)


@pytest.mark.asyncio
async def test_get_oauth_url_unsupported_provider_raises_error(
    mock_factory: MagicMock,
    mock_cache: MagicMock,
) -> None:
    mock_factory.get_service.return_value = None
    use_case = GetOAuthUrlUseCase(factory=mock_factory, cache=mock_cache)

    with pytest.raises(OAuthProviderNotSupportedError):
        await use_case.execute(provider="unsupported_provider")

    mock_factory.get_service.assert_called_once_with("unsupported_provider")
    mock_cache.set.assert_not_awaited()