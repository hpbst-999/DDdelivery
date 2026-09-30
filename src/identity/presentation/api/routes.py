import secrets

from fastapi import APIRouter, Depends, HTTPException, Query

from src.identity.application.interfaces import IOAuthServiceFactory
from src.identity.application.use_cases.login_oauth import LoginWithOAuthUseCase
from src.identity.application.use_cases.logout import LogoutUseCase
from src.identity.application.use_cases.refresh_session import RefreshSessionUseCase
from src.identity.application.use_cases.request_otp import RequestOTPUseCase
from src.identity.domain.entities.account import Account
from src.identity.domain.exceptions import DomainException
from src.identity.presentation.api.schemas import (
    LogoutRequest,
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
    get_current_account,
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

router = APIRouter(tags=["Authentication"])

@router.post("/otp/request", response_model=ResponseOTP)
async def send_code(
    request: RequestOTP,
    use_case: RequestOTPUseCase = Depends(get_request_otp_use_case)
):
    try:
        session_id = await use_case.execute(raw_phone_number=request.phone)
        return ResponseOTP(session_id=str(session_id))

    except DomainException as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/otp/verify", response_model=TokenResponse)
async def verify_user_otp(
    request: VerifyOTPRequest,
    use_case = Depends(get_verify_otp_use_case)
):
    try:
        tokens = await use_case.execute(session_id=request.session_id, input_code=request.code)
        return TokenResponse(
            access_token=tokens["access_token"],
            refresh_token=tokens["refresh_token"]
        )

    except DomainException as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    request: RefreshRequest,
    use_case: RefreshSessionUseCase = Depends(get_refresh_session_use_case)
):
    try:
        tokens = await use_case.execute(raw_refresh_token=request.refresh_token)

        return TokenResponse(
            access_token=tokens["access_token"],
            refresh_token=tokens["refresh_token"]
        )
    except DomainException as e:
        raise HTTPException(status_code=401, detail=str(e))


@router.post("/logout")
async def logout(
    request: LogoutRequest,
    use_case: LogoutUseCase = Depends(get_logout_use_case)
):
    try:
        await use_case.execute(refresh_token=request.refresh_token)
    except DomainException:
        pass

    return {"message": "successful logout"}


@router.get("/user/me", response_model=UserProfileResponse)
async def get_user_profile(
    account: Account = Depends(get_current_account),
    use_case = Depends(get_user_profile_use_case)
):
    try:
        profile = await use_case.execute(profile_id=account.id)
        return profile
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception :
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.patch("/user/me", response_model=UserProfileResponse)
async def update_user_profile(
    data: UpdateUserProfileRequest,
    account: Account = Depends(get_current_account),
    use_case = Depends(get_update_user_profile_use_case)
):
    try:
        profile = await use_case.execute(
            account_id=account.id,
            name=data.name,
            address=data.address
        )
        return profile
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception :
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.delete("/user/me", status_code=204)
async def delete_user_account(
    account: Account = Depends(get_current_account),
    use_case = Depends(get_delete_account_use_case)
):
    try:
        await use_case.execute(account_id=account.id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get("/{provider}/url")
async def get_user_auth_url(
    provider:str,
    factory = Depends(get_oauth_service_factory),
    cache= Depends(get_cache_repository)
):
    try:
        oauth_service = factory.get_service(provider)

    except ValueError as exc:
        raise HTTPException(
            status_code=400, detail=str(exc))
    state = secrets.token_urlsafe(16)
    cache_key = f"state:{state}"
    await cache.set(key=cache_key, value=provider)
    url = oauth_service.get_authorization_url(state)
    return {"url": url}

@router.get("/{provider}/callback")
async def user_oauth_callback(
    provider: str,
    code: str = Query(..., description="Authorization code"),
    state: str | None = Query(None),
    factory: IOAuthServiceFactory = Depends(get_oauth_service_factory),
    use_case: LoginWithOAuthUseCase = Depends(get_login_user_use_case),
    cache = Depends(get_cache_repository)
):
    cache_key = f"oauth_state:{state}"
    saved_provider= await cache.get(key=cache_key)
    if not saved_provider:
        raise HTTPException(status_code=400, detail="State is invalid or expired.")
    await cache.delete(key=cache_key)
    if saved_provider != provider:
        raise HTTPException(status_code=400, detail="State provider mismatch.")
    oauth_service = factory.get_service(provider)
    user_info = await oauth_service.get_user_info(code=code, role="user")
    return await use_case.execute(user_info)
