from fastapi import Depends,HTTPException, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import redis
from src.core.database import SessionFactory
from src.identity.domain.entities.account import Account
from src.identity.application.interfaces import IUnitOfWork
from src.identity.application.use_cases.request_otp import RequestOTPUseCase
from src.identity.application.use_cases.refresh_session import RefreshSessionUseCase
from src.identity.application.use_cases.logout import LogoutUseCase
from src.identity.application.use_cases.verify_otp_and_create_courier_account import VerifyOTPUAndCreateCourierUseCase
from src.identity.application.use_cases.verify_otp_and_create_user_account import VerifyOTPUAndCreateUserUseCase
from src.identity.application.use_cases.update_courier_profile import UpdateCourierProfileUseCase
from src.identity.application.use_cases.update_user_profile import UpdateUserProfileUseCase
from src.identity.application.use_cases.delete_courier import DeleteCourierUseCase
from src.identity.application.use_cases.delete_user import DeleteUserUseCase
from src.identity.application.use_cases.get_courier_profile import GetCourierProfileUseCase
from src.identity.application.use_cases.get_user_profile import GetUserProfileUseCase
from src.identity.infrastructure.uow import SQLAlchemyUnitOfWork
# from src.identity.infrastructure.uow import RedisUnitOfWork
from src.identity.infrastructure.sms_service import SmsSender
from src.identity.infrastructure.security_jwt import JwtTokenService
from src.core.config import settings
from typing import Iterator
from sqlalchemy.orm import Session

redis_client = redis.Redis(
    host=settings.REDIS_HOST, 
    port=settings.REDIS_PORT, 
    db=settings.REDIS_DB
)
def get_db() -> Iterator[Session]:

    session = SessionFactory()
    try:
        yield session
    except Exception as e:
        session.rollback()  
        raise  
    finally:
        session.close()

def get_pg_uow(session: Session = Depends(get_db)) -> IUnitOfWork:
    return SQLAlchemyUnitOfWork(session=session)

def get_token_service() -> JwtTokenService:
    return JwtTokenService(secret_key=settings.JWT_SECRET_KEY)

def get_sms_sender() -> SmsSender:
    return SmsSender()

# def get_redis_uow() -> RedisUnitOfWork:
#     return RedisUnitOfWork(redis_client=redis_client)

def get_request_otp_use_case(
    uow: IUnitOfWork = Depends(get_pg_uow),
    sms_gateway: SmsSender = Depends(get_sms_sender)
) -> RequestOTPUseCase:
    return RequestOTPUseCase(uow=uow, sms_gateway=sms_gateway)

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
) -> VerifyOTPUAndCreateUserUseCase:
    return VerifyOTPUAndCreateUserUseCase(
        uow=uow, 
        token_service=token_service
    )

def get_update_courier_profile_use_case(
    uow: IUnitOfWork = Depends(get_pg_uow)
) -> UpdateCourierProfileUseCase:
    return UpdateCourierProfileUseCase(uow=uow)

def get_update_user_profile_use_case(
    uow: IUnitOfWork = Depends(get_pg_uow)
) -> UpdateUserProfileUseCase:
    return UpdateUserProfileUseCase(uow=uow)

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
    uow: IUnitOfWork = Depends(get_pg_uow)
) -> GetUserProfileUseCase:
    return GetUserProfileUseCase(uow=uow)

security = HTTPBearer()
def get_current_account(
    credentials: HTTPAuthorizationCredentials = Depends(security), 
    token_service: JwtTokenService = Depends(get_token_service),
    uow: IUnitOfWork = Depends(get_pg_uow)
) -> Account:
    token = credentials.credentials
    try:
        payload = token_service.validate_access_token(token) 
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    account_id = payload.get("sub")
    if not account_id:
        raise HTTPException(status_code=401, detail="No ID found in token")
    
    with uow:
        account = uow.accounts.get_account_by_id(account_id)
        if not account:
            raise HTTPException(status_code=401, detail="Account not found")
        
        return account