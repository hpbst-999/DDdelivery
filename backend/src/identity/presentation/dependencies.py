from collections.abc import AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import settings
from src.core.database import SessionFactory, redis_client
from src.identity.application.interfaces import (
    ICacheRepository,
    IOAuthService,
    IOAuthServiceFactory,
    IUnitOfWork,
)
from src.identity.application.use_cases.delete_account import DeleteAccountUseCase
from src.identity.application.use_cases.get_user_profile import GetUserProfileUseCase
from src.identity.application.use_cases.login_oauth import LoginWithOAuthUseCase
from src.identity.application.use_cases.logout import LogoutUseCase
from src.identity.application.use_cases.refresh_session import RefreshSessionUseCase
from src.identity.application.use_cases.request_otp import RequestOTPUseCase
from src.identity.application.use_cases.update_user_profile import UpdateUserProfileUseCase
from src.identity.application.use_cases.verify_otp_and_create_account import (
    VerifyOTPAndCreateAccountUseCase,
)
from src.identity.infrastructure.google_service import GoogleOAuthService
from src.identity.infrastructure.oauth_factory import OAuthServiceFactory
from src.identity.infrastructure.redis_repositories import RedisCacheRepository
from src.identity.infrastructure.security_jwt import JwtTokenService
from src.identity.infrastructure.uow import SQLAlchemyUnitOfWork
from src.identity.infrastructure.yandex_service import YandexOAuthService


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with SessionFactory() as session:
        yield session


def get_uow(session: AsyncSession = Depends(get_db)) -> IUnitOfWork:
    return SQLAlchemyUnitOfWork(session=session)


def get_token_service() -> JwtTokenService:
    return JwtTokenService(secret_key=settings.JWT_SECRET_KEY)


def get_cache_repository() -> ICacheRepository:
    return RedisCacheRepository(redis_client=redis_client)


def get_request_otp_use_case(uow: IUnitOfWork = Depends(get_uow)) -> RequestOTPUseCase:
    return RequestOTPUseCase(uow=uow)


def get_refresh_session_use_case(
    uow: IUnitOfWork = Depends(get_uow), token_service: JwtTokenService = Depends(get_token_service)
) -> RefreshSessionUseCase:
    return RefreshSessionUseCase(uow=uow, token_service=token_service)


def get_logout_use_case(uow: IUnitOfWork = Depends(get_uow)) -> LogoutUseCase:
    return LogoutUseCase(uow=uow)


def get_verify_otp_use_case(
    uow: IUnitOfWork = Depends(get_uow), token_service: JwtTokenService = Depends(get_token_service)
) -> VerifyOTPAndCreateAccountUseCase:
    return VerifyOTPAndCreateAccountUseCase(uow=uow, token_service=token_service)


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
    return GoogleOAuthService()


def get_yandex_oauth_service() -> IOAuthService:
    return YandexOAuthService()


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


def get_login_user_use_case(
    uow: IUnitOfWork = Depends(get_uow),
    token_service: JwtTokenService = Depends(get_token_service),
) -> LoginWithOAuthUseCase:
    return LoginWithOAuthUseCase(uow=uow, token_service=token_service)
