import secrets

from src.identity.application.interfaces import ICacheRepository, IOAuthServiceFactory
from src.identity.domain.exceptions import OAuthProviderNotSupportedError


class GetOAuthUrlUseCase:
    def __init__(self, factory: IOAuthServiceFactory, cache: ICacheRepository):
        self.factory = factory
        self.cache = cache

    async def execute(self, provider: str) -> str:
        oauth_service = self.factory.get_service(provider)
        if not oauth_service:
            raise OAuthProviderNotSupportedError

        state = secrets.token_urlsafe(16)
        cache_key = f"state:{state}"
        await self.cache.set(key=cache_key, value=provider, ttl_second=600)
        url = oauth_service.get_authorization_url(state)
        return url
