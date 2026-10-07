from src.identity.application.interfaces import (
    ICacheRepository,
    IOAuthServiceFactory,
    ITokenGenerator,
    IUnitOfWork,
)
from src.identity.domain.exceptions import DomainException
from src.identity.domain.value_objects.email import Email


class LoginWithOAuthUseCase:
    def __init__(
        self,
        uow: IUnitOfWork,
        token_generator: ITokenGenerator,
        factory: IOAuthServiceFactory,
        cache: ICacheRepository,
    ):
        self.uow = uow
        self.token_generator = token_generator
        self.factory = factory
        self.cache = cache

    async def execute(self, state: str, provider: str, code: str) -> Email:
        cache_key = f"state:{state}"
        saved_provider = await self.cache.get(key=cache_key)
        if not saved_provider:
            raise DomainException("State is invalid or expired")
        await self.cache.delete(key=cache_key)
        if saved_provider != provider:
            raise DomainException("State provider mismatch")
        oauth_service = self.factory.get_service(provider)
        user_info = await oauth_service.get_user_info(code=code)
        return Email(user_info.email)
