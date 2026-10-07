import secrets

from fastapi import APIRouter, Depends, HTTPException, Query, status

from src.identity.application.interfaces import TokenPair
from src.identity.application.use_cases.create_account import CreateAccountUseCase
from src.identity.application.use_cases.delete_account import DeleteAccountUseCase
from src.identity.application.use_cases.get_user_profile import GetUserProfileUseCase
from src.identity.application.use_cases.login_oauth import LoginWithOAuthUseCase
from src.identity.application.use_cases.logout import LogoutUseCase
from src.identity.application.use_cases.refresh_session import RefreshSessionUseCase
from src.identity.application.use_cases.request_otp import RequestOTPUseCase
from src.identity.application.use_cases.update_user_profile import UpdateUserProfileUseCase
from src.identity.application.use_cases.verify_otp import VerifyOTPUseCase
from src.identity.domain.entities.account import Account
from src.identity.domain.exceptions import (
    AccountNotFoundError,
    DomainException,
    InvalidOTPCodeError,
    InvalidTokenError,
    OTPRateLimitError,
    OTPSessionNotFoundError,
    ProfileNotFoundError,
    SessionNotFoundError,
    TokenExpiredError,
)
from src.identity.presentation.api.schemas import (
    LogoutRequest,
    OAuthUrlResponse,
    RefreshRequest,
    RequestOTP,
    ResponseOTP,
    TokenResponse,
    UpdateUserProfileRequest,
    UserProfileResponse,
    VerifyOTPRequest,
)
from src.identity.presentation.dependencies import (
    get_cache_repository,
    get_create_account_use_case,
    get_delete_account_use_case,
    get_login_user_use_case,
    get_logout_use_case,
    get_oauth_service_factory,
    get_refresh_session_use_case,
    get_request_otp_use_case,
    get_update_user_profile_use_case,
    get_user_profile_use_case,
    get_verify_otp_use_case,
)
from src.identity.presentation.security import get_current_account

router = APIRouter(tags=["Authentication"])


@router.post("/otp/request", response_model=ResponseOTP)
async def send_code(
    request: RequestOTP, use_case: RequestOTPUseCase = Depends(get_request_otp_use_case)
) -> ResponseOTP:
    try:
        session_id = await use_case.execute(raw_phone_number=request.phone)
        return session_id

    except OTPRateLimitError:
        HTTPException(status_code=status.HTTP_400_BAD_REQUEST)


@router.post("/otp/verify", response_model=TokenResponse)
async def verify_user_otp(
    request: VerifyOTPRequest,
    verify_use_case: VerifyOTPUseCase = Depends(get_verify_otp_use_case),
    create_account_use_case: CreateAccountUseCase = Depends(get_create_account_use_case),
) -> TokenResponse:
    try:
        phone_number = await verify_use_case.execute(
            session_id=request.session_id, input_code=request.code
        )
        tokens = await create_account_use_case.execute(phone_number)
        return TokenPair(access_token=tokens.access_token, refresh_token=tokens.refresh_token)

    except OTPSessionNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    except InvalidOTPCodeError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    request: RefreshRequest, use_case: RefreshSessionUseCase = Depends(get_refresh_session_use_case)
) -> TokenResponse:
    try:
        tokens = await use_case.execute(raw_refresh_token=request.refresh_token)

        return TokenPair(access_token=tokens.access_token, refresh_token=tokens.refresh_token)
    except (InvalidTokenError, SessionNotFoundError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    except TokenExpiredError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    request: LogoutRequest, use_case: LogoutUseCase = Depends(get_logout_use_case)
) -> None:
    try:
        await use_case.execute(refresh_token=request.refresh_token)
    except DomainException:
        pass


@router.get("/user/me", response_model=UserProfileResponse)
async def get_user_profile(
    account: Account = Depends(get_current_account),
    use_case: GetUserProfileUseCase = Depends(get_user_profile_use_case),
) -> UserProfileResponse:
    try:
        profile = await use_case.execute(account_id=account.id)
        return profile
    except ProfileNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)


@router.patch("/user/me", response_model=UserProfileResponse)
async def update_user_profile(
    data: UpdateUserProfileRequest,
    account: Account = Depends(get_current_account),
    use_case: UpdateUserProfileUseCase = Depends(get_update_user_profile_use_case),
) -> UserProfileResponse:
    try:
        profile = await use_case.execute(
            account_id=account.id, name=data.name, address=data.address
        )
        return profile
    except ProfileNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)


@router.delete("/user/me", status_code=204)
async def delete_user_account(
    account: Account = Depends(get_current_account),
    use_case: DeleteAccountUseCase = Depends(get_delete_account_use_case),
) -> None:
    try:
        await use_case.execute(account_id=account.id)
    except AccountNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)


@router.get("/{provider}/url", response_model=OAuthUrlResponse)
async def get_user_auth_url(
    provider: str, factory=Depends(get_oauth_service_factory), cache=Depends(get_cache_repository)
) -> OAuthUrlResponse:
    try:
        oauth_service = factory.get_service(provider)

    except ValueError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    state = secrets.token_urlsafe(16)
    cache_key = f"state:{state}"
    await cache.set(key=cache_key, value=provider)
    url = oauth_service.get_authorization_url(state)
    return OAuthUrlResponse(url=url)


@router.get("/{provider}/callback", response_model=TokenResponse)
async def user_oauth_callback(
    provider: str,
    code: str = Query(..., description="Authorization code"),
    state: str | None = Query(None),
    login_use_case: LoginWithOAuthUseCase = Depends(get_login_user_use_case),
    create_account_use_case: CreateAccountUseCase = Depends(get_create_account_use_case),
) -> TokenResponse:
    try:
        email = await login_use_case.execute(state=state, provider=provider, code=code)
        tokens = await create_account_use_case.execute(email=email)
    except ValueError:
        raise HTTPException

    return tokens
