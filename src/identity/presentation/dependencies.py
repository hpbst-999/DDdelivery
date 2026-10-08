from collections.abc import AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import settings
from src.core.database import SessionFactory, redis_client
from src.identity.application.interfaces import (
    ICacheRepository,
    IOAuthService,
    IOAuthServiceFactory,
    ITokenGenerator,
    ITokenValidator,
    IUnitOfWork,
)
from src.identity.application.use_cases.create_account import CreateAccountUseCase
from src.identity.application.use_cases.delete_account import DeleteAccountUseCase
from src.identity.application.use_cases.get_oauth_url import GetOAuthUrlUseCase
from src.identity.application.use_cases.get_user_profile import GetUserProfileUseCase
from src.identity.application.use_cases.login_oauth import LoginWithOAuthUseCase
from src.identity.application.use_cases.logout import LogoutUseCase
from src.identity.application.use_cases.refresh_session import RefreshSessionUseCase
from src.identity.application.use_cases.request_otp import RequestOTPUseCase
from src.identity.application.use_cases.update_user_profile import UpdateUserProfileUseCase
from src.identity.application.use_cases.verify_otp import VerifyOTPUseCase
from src.identity.infrastructure.adapters.oauth.google_service import GoogleOAuthService
from src.identity.infrastructure.adapters.oauth.oauth_factory import OAuthServiceFactory
from src.identity.infrastructure.adapters.oauth.yandex_service import YandexOAuthService
from src.identity.infrastructure.redis_repositories import RedisCacheRepository
from src.identity.infrastructure.security_jwt import TokenGenerator, TokenValidator
from src.identity.infrastructure.uow import UnitOfWork


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with SessionFactory() as session:
        yield session


def get_uow(session: AsyncSession = Depends(get_db)) -> IUnitOfWork:
    return UnitOfWork(session=session)


def get_token_generator() -> ITokenGenerator:
    return TokenGenerator(
        secret_key=settings.JWT_SECRET_KEY,
        access_token_expire_minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES,
        refresh_token_expire_minutes=settings.REFRESH_TOKEN_EXPIRE_DAYS,
    )


def get_token_validator() -> ITokenValidator:
    return TokenValidator(secret_key=settings.JWT_SECRET_KEY)


def get_cache_repository() -> ICacheRepository:
    return RedisCacheRepository(redis_client=redis_client)


def get_request_otp_use_case(uow: IUnitOfWork = Depends(get_uow)) -> RequestOTPUseCase:
    return RequestOTPUseCase(uow=uow)


def get_create_account_use_case(
    uow: IUnitOfWork = Depends(get_uow),
    token_generator: ITokenGenerator = Depends(get_token_generator),
) -> CreateAccountUseCase:
    return CreateAccountUseCase(uow=uow, token_generator=token_generator)


def get_refresh_session_use_case(
    uow: IUnitOfWork = Depends(get_uow),
    token_generator: TokenGenerator = Depends(get_token_generator),
    token_validator: TokenValidator = Depends(TokenValidator),
) -> RefreshSessionUseCase:
    return RefreshSessionUseCase(
        uow=uow, token_generator=token_generator, token_validator=token_validator
    )


def get_logout_use_case(uow: IUnitOfWork = Depends(get_uow)) -> LogoutUseCase:
    return LogoutUseCase(uow=uow)


def get_verify_otp_use_case(uow: IUnitOfWork = Depends(get_uow)) -> VerifyOTPUseCase:
    return VerifyOTPUseCase(
        uow=uow,
    )


def get_update_user_profile_use_case(
    uow: IUnitOfWork = Depends(get_uow), cache: ICacheRepository = Depends(get_cache_repository)
) -> UpdateUserProfileUseCase:
    return UpdateUserProfileUseCase(uow=uow, cache=cache)


def get_delete_account_use_case(uow: IUnitOfWork = Depends(get_uow)) -> DeleteAccountUseCase:
    return DeleteAccountUseCase(uow=uow)


def get_user_profile_use_case(
    uow: IUnitOfWork = Depends(get_uow), cache: ICacheRepository = Depends(get_cache_repository)
) -> GetUserProfileUseCase:
    return GetUserProfileUseCase(uow=uow, cache=cache)


def get_google_oauth_service() -> IOAuthService:
    return GoogleOAuthService(
        client_id=settings.YANDEX_CLIENT_ID, client_secret=settings.YANDEX_CLIENT_SECRET
    )


def get_yandex_oauth_service() -> IOAuthService:
    return YandexOAuthService(
        client_id=settings.YANDEX_CLIENT_ID, client_secret=settings.YANDEX_CLIENT_SECRET
    )


def get_oauth_service_factory(
    google_service: IOAuthService = Depends(get_google_oauth_service),
    yandex_service: IOAuthService = Depends(get_yandex_oauth_service),
) -> IOAuthServiceFactory:
    return OAuthServiceFactory(
        services={
            "google": google_service,
            "yandex": yandex_service,
        }
    )


def get_oauth_url(
    factory: IOAuthServiceFactory = Depends(get_oauth_service_factory),
    cache: ICacheRepository = Depends(get_cache_repository),
) -> GetOAuthUrlUseCase:
    return GetOAuthUrlUseCase(factory=factory, cache=cache)


def get_login_user_use_case(
    uow: IUnitOfWork = Depends(get_uow),
    factory: IOAuthServiceFactory = Depends(get_oauth_service_factory),
    cache: ICacheRepository = Depends(get_cache_repository),
) -> LoginWithOAuthUseCase:
    return LoginWithOAuthUseCase(
        uow=uow, factory=factory, cache=cache
    )
