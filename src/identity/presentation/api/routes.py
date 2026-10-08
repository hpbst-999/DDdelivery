from fastapi import APIRouter, Depends, HTTPException, Query, status

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
from src.identity.domain.entities.account import Account
from src.identity.domain.exceptions import (
    AccountNotFoundError,
    DomainException,
    InvalidCredentialsError,
    InvalidOAuthStateError,
    InvalidOTPCodeError,
    InvalidTokenError,
    OAuthProviderNotSupportedError,
    OAuthStateMismatchError,
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
    get_create_account_use_case,
    get_delete_account_use_case,
    get_login_user_use_case,
    get_logout_use_case,
    get_oauth_url,
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
    except OTPRateLimitError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
    return ResponseOTP.model_validate(session_id)


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

    except OTPSessionNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    except InvalidOTPCodeError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
    return TokenResponse.model_validate(tokens)


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    request: RefreshRequest, use_case: RefreshSessionUseCase = Depends(get_refresh_session_use_case)
) -> TokenResponse:
    try:
        tokens = await use_case.execute(raw_refresh_token=request.refresh_token)
        
    except (InvalidTokenError, SessionNotFoundError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    except TokenExpiredError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    return TokenResponse.model_validate(tokens)

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
    except ProfileNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return UserProfileResponse.model_validate(profile)

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
    except ProfileNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return UserProfileResponse.model_validate(profile)

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
    provider: str, use_case: GetOAuthUrlUseCase = Depends(get_oauth_url)
) -> OAuthUrlResponse:
    try:
        url = await use_case.execute(provider=provider)
    except OAuthProviderNotSupportedError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    return OAuthUrlResponse.model_validate(url)


@router.get("/{provider}/callback", response_model=TokenResponse)
async def user_oauth_callback(
    provider: str,
    code: str = Query(..., description="Authorization code"),
    state: str  = Query(...),
    login_use_case: LoginWithOAuthUseCase = Depends(get_login_user_use_case),
    create_account_use_case: CreateAccountUseCase = Depends(get_create_account_use_case),
) -> TokenResponse:
    try:
        email = await login_use_case.execute(state=state, provider=provider, code=code)
        tokens = await create_account_use_case.execute(email=email)
    except (InvalidOAuthStateError, OAuthStateMismatchError):
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT)

    except InvalidCredentialsError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)

    return TokenResponse.model_validate(tokens)
