from redis.asyncio import Redis
from collections.abc import AsyncGenerator
from uuid import UUID

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import settings
from src.core.database import SessionFactory
from src.core.database import redis_client
from src.identity.application.interfaces import IOAuthService, IUnitOfWork
from src.identity.application.use_cases.delete_courier import DeleteCourierUseCase
from src.identity.application.use_cases.delete_user import DeleteUserUseCase
from src.identity.application.use_cases.get_courier_profile import GetCourierProfileUseCase
from src.identity.application.use_cases.get_user_profile import GetUserProfileUseCase
from src.identity.application.use_cases.login_courier_oauth import LoginCourierWithOAuthUseCase
from src.identity.application.use_cases.login_user_oauth import LoginUserWithOAuthUseCase
from src.identity.application.use_cases.logout import LogoutUseCase
from src.identity.application.use_cases.refresh_session import RefreshSessionUseCase
from src.identity.application.use_cases.request_otp import RequestOTPUseCase
from src.identity.application.use_cases.update_courier_profile import UpdateCourierProfileUseCase
from src.identity.application.use_cases.update_user_profile import UpdateUserProfileUseCase
from src.identity.application.use_cases.verify_otp_and_create_courier_account import VerifyOTPUAndCreateCourierUseCase
from src.identity.application.use_cases.verify_otp_and_create_user_account import VerifyOTPAndCreateUserUseCase
from src.identity.domain.entities.account import Account
from src.identity.infrastructure.google_service import GoogleOAuthService
from src.identity.infrastructure.security_jwt import JwtTokenService
from src.identity.infrastructure.uow import SQLAlchemyUnitOfWork
from src.identity.infrastructure.yandex_service import YandexOAuthService
from src.identity.application.interfaces import ICacheRepository
from src.identity.infrastructure.redis_repositories import RedisCacheRepository


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with SessionFactory() as session:
        yield session


def get_pg_uow(session: AsyncSession = Depends(get_db)) -> IUnitOfWork:
    return SQLAlchemyUnitOfWork(session=session)

def get_token_service() -> JwtTokenService:
    return JwtTokenService(secret_key=settings.JWT_SECRET_KEY)


def get_redis_repository() -> ICacheRepository:
    return RedisCacheRepository(redis_client=redis_client)

def get_request_otp_use_case(
    uow: IUnitOfWork = Depends(get_pg_uow)
) -> RequestOTPUseCase:
    return RequestOTPUseCase(uow=uow)

def get_refresh_session_use_case(
    uow: IUnitOfWork = Depends(get_pg_uow),
    token_service: JwtTokenService = Depends(get_token_service)
) -> RefreshSessionUseCase:
    return RefreshSessionUseCase(uow=uow, token_service=token_service)

def get_logout_use_case(
    uow: IUnitOfWork = Depends(get_pg_uow)
) -> LogoutUseCase:
    return LogoutUseCase(uow=uow)

def get_verify_courier_otp_use_case(
    uow: IUnitOfWork = Depends(get_pg_uow),
    token_service: JwtTokenService = Depends(get_token_service)
) -> VerifyOTPUAndCreateCourierUseCase:
    return VerifyOTPUAndCreateCourierUseCase(
        uow=uow, 
        token_service=token_service
    )

def get_verify_user_otp_use_case(
    uow: IUnitOfWork = Depends(get_pg_uow),
    token_service: JwtTokenService = Depends(get_token_service)
) -> VerifyOTPAndCreateUserUseCase:
    return VerifyOTPAndCreateUserUseCase(
        uow=uow, 
        token_service=token_service
    )

def get_update_courier_profile_use_case(
    uow: IUnitOfWork = Depends(get_pg_uow)
) -> UpdateCourierProfileUseCase:
    return UpdateCourierProfileUseCase(uow=uow)

def get_update_user_profile_use_case(
    uow: IUnitOfWork = Depends(get_pg_uow),
    cache: ICacheRepository = Depends(get_redis_repository)
) -> UpdateUserProfileUseCase:
    return UpdateUserProfileUseCase(uow=uow, cache=cache)

def get_delete_courier_use_case(
    uow: IUnitOfWork = Depends(get_pg_uow)
) -> DeleteCourierUseCase:
    return DeleteCourierUseCase(uow=uow)

def get_delete_user_use_case(
    uow: IUnitOfWork = Depends(get_pg_uow)
) -> DeleteUserUseCase:
    return DeleteUserUseCase(uow=uow)

def get_courier_profile_use_case(
    uow: IUnitOfWork = Depends(get_pg_uow)
) -> GetCourierProfileUseCase:
    return GetCourierProfileUseCase(uow=uow)

def get_user_profile_use_case(
    uow: IUnitOfWork = Depends(get_pg_uow),
    cache: ICacheRepository = Depends(get_redis_repository)
) -> GetUserProfileUseCase:
    return GetUserProfileUseCase(uow=uow, cache=cache)

security = HTTPBearer()
async def get_current_account(
    credentials: HTTPAuthorizationCredentials = Depends(security), 
    token_service: JwtTokenService = Depends(get_token_service),
    uow: IUnitOfWork = Depends(get_pg_uow),
    cache: ICacheRepository = Depends(get_redis_repository)
) -> Account:
    token = credentials.credentials
    try:
        payload = token_service.validate_access_token(token) 
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    account_id = UUID(payload.get("sub"))
    if not account_id:
        raise HTTPException(status_code=401, detail="No ID found in token")

    cache_key = f"account:{account_id}"
    cache_account = await cache.get(key=cache_key)
    if cache_account:
        return Account.from_dict(cache_account)
    
    async with uow:
        account = await uow.accounts.get_account_by_id(account_id)
        if not account:
            raise HTTPException(status_code=401, detail="Account not found")
        await cache.set(cache_key, account.to_dict(), ttl_second=600)
        
        return account

def get_google_oauth_service() -> IOAuthService:
    return GoogleOAuthService()


def get_yandex_oauth_service() -> IOAuthService:
    return YandexOAuthService()

def get_login_user_use_case(
    uow: IUnitOfWork = Depends(get_pg_uow),
    token_service: JwtTokenService = Depends(get_token_service),
) -> LoginUserWithOAuthUseCase:
    return LoginUserWithOAuthUseCase(uow=uow, token_service=token_service)


def get_login_courier_use_case(
    uow: IUnitOfWork = Depends(get_pg_uow),
    token_service: JwtTokenService = Depends(get_token_service),
) -> LoginCourierWithOAuthUseCase:
    return LoginCourierWithOAuthUseCase(uow=uow, token_service=token_service)