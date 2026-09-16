from fastapi import APIRouter, Depends, HTTPException, Query

from src.identity.application.interfaces import IOAuthService
from src.identity.application.use_cases.login_courier_oauth import LoginCourierWithOAuthUseCase
from src.identity.application.use_cases.login_user_oauth import LoginUserWithOAuthUseCase
from src.identity.application.use_cases.logout import LogoutUseCase
from src.identity.application.use_cases.refresh_session import RefreshSessionUseCase
from src.identity.application.use_cases.request_otp import RequestOTPUseCase
from src.identity.domain.entities.account import Account
from src.identity.domain.entities.courier_profile import CourierProfile
from src.identity.domain.entities.user_profile import UserProfile
from src.identity.domain.exceptions import DomainException
from src.identity.presentation.api.schemas import (
    CourierProfileResponse,
    LogoutRequest,
    RefreshRequest,
    RequestOTP,
    ResponseOTP,
    TokenResponse,
    UpdateCourierProfileRequest,
    UpdateUserProfileRequest,
    UserProfileResponse,
    VerifyOTPRequest,
)
from src.identity.presentation.dependencies import (
    get_courier_profile_use_case,
    get_current_account,
    get_delete_courier_use_case,
    get_delete_user_use_case,
    get_google_oauth_service,
    get_login_courier_use_case,
    get_login_user_use_case,
    get_logout_use_case,
    get_refresh_session_use_case,
    get_request_otp_use_case,
    get_update_courier_profile_use_case,
    get_update_user_profile_use_case,
    get_user_profile_use_case,
    get_verify_courier_otp_use_case,
    get_verify_user_otp_use_case,
    get_yandex_oauth_service,
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
    
@router.post("/verify/user", response_model=TokenResponse)
async def verify_user_otp(
    request: VerifyOTPRequest,
    use_case = Depends(get_verify_user_otp_use_case)
):
    try:
        tokens = await use_case.execute(session_id=request.session_id, input_code=request.code)
        return TokenResponse(
            access_token=tokens["access_token"],
            refresh_token=tokens["refresh_token"]
        )
    
    except DomainException as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@router.post("/verify/courier", response_model=TokenResponse)
async def verify_courier_otp(
    request: VerifyOTPRequest,
    use_case = Depends(get_verify_courier_otp_use_case)
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
    use_case = Depends(get_delete_user_use_case)
):
    try:
        await use_case.execute(account_id=account.id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error")
    
@router.get("/courier/me", response_model=CourierProfileResponse)
async def get_courier_profile(
    account: Account = Depends(get_current_account),
    use_case = Depends(get_courier_profile_use_case)
):
    try:
        profile = await use_case.execute(account_id=account.id)
        return profile
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="Internal Server Error")
    
@router.patch("/courier/me", response_model=CourierProfileResponse)
async def update_courier_profile(
    data: UpdateCourierProfileRequest,
    account: Account = Depends(get_current_account),
    use_case = Depends(get_update_courier_profile_use_case)
):
    try:
        profile = await use_case.execute(account_id=account.id, name=data.name)
        return profile
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500,detail="Internal Server Error")


@router.delete("/courier/me", status_code=204)
async def delete_courier_account(
    account: Account = Depends(get_current_account),
    use_case = Depends(get_delete_courier_use_case)
):
    try:
        await use_case.execute(account_id=account.id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get("/user/google/url")
def get_user_google_url(
    redirect_uri: str = Query(..., description="Callback URL"),
    oauth_service: IOAuthService = Depends(get_google_oauth_service),
):
    url = oauth_service.get_authorization_url(
        redirect_uri=redirect_uri, state="csrf_token"
    )
    return {"url": url}


@router.get("/user/google/callback")
async def user_google_callback(
    code: str = Query("http://localhost:8000/api/v1/auth/user/google/callback", description="code Google"),
    state: str | None = Query(None),
    oauth_service: IOAuthService = Depends(get_google_oauth_service),
    use_case: LoginUserWithOAuthUseCase = Depends(get_login_user_use_case),
):
    try:
        user_info = await oauth_service.get_user_info(code, "http://localhost:8000/api/v1/auth/user/google/callback")
    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail=f"Google auth failed: {exc}",
        )
    return await use_case.execute(user_info)

@router.get("/callback")
def google_callback():
    return {"message": "Успешный вход через Google"}

@router.get("/user/yandex/url")
def get_yandex_auth_url(
    redirect_uri: str = Query("http://localhost:8000/api/v1/auth/user/yandex/callback", description="Callback URL"),
    oauth_service: IOAuthService = Depends(get_yandex_oauth_service),
):
    url = oauth_service.get_authorization_url(
        redirect_uri=redirect_uri, state="dev_state"
    )
    return {"url": url}


@router.get("/user/yandex/callback")
async def yandex_callback(
    code: str = Query(..., description="code yandex"),
    state: str | None = Query(None),
    oauth_service: IOAuthService = Depends(get_yandex_oauth_service),
    use_case: LoginUserWithOAuthUseCase = Depends(get_login_user_use_case),
):
    try:
        user_info = await oauth_service.get_user_info(
            code=code, redirect_uri="http://localhost:8000/api/v1/auth/user/google/callback"
        )
    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail=f"Yandex auth failed: {exc}",
        )

    return await use_case.execute(user_info)

@router.get("/courier/google/url")
def get_courier_google_auth_url(
    redirect_uri: str = Query(
        "http://localhost:8000/api/v1/auth/courier/google/callback",
        description="Callback URL",
    ),
    oauth_service: IOAuthService = Depends(get_google_oauth_service),
):
    url = oauth_service.get_authorization_url(
        redirect_uri=redirect_uri, state="courier_dev_state"
    )
    return {"url": url}


@router.get("/courier/google/callback")
async def courier_google_callback(
    code: str = Query(..., description="Authorization code от Google"),
    state: str | None = Query(None),
    oauth_service: IOAuthService = Depends(get_google_oauth_service),
    use_case: LoginCourierWithOAuthUseCase = Depends(
        get_login_courier_use_case
    ),
):
    try:
        user_info = await oauth_service.get_user_info(
            code=code,
            redirect_uri="http://localhost:8000/api/v1/auth/courier/google/callback",
        )
    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail=f"Google courier auth failed: {exc}",
        )

    return await use_case.execute(user_info)

@router.get("/courier/yandex/url")
def get_courier_yandex_auth_url(
    redirect_uri: str = Query(
        "http://localhost:8000/api/v1/auth/courier/yandex/callback",
        description="Callback URL для курьера",
    ),
    oauth_service: IOAuthService = Depends(get_yandex_oauth_service),
):
    url = oauth_service.get_authorization_url(
        redirect_uri=redirect_uri, state="courier_dev_state"
    )
    return {"url": url}


@router.get("/courier/yandex/callback")
async def courier_yandex_callback(
    code: str = Query(..., description="Authorization code от Яндекса"),
    state: str | None = Query(None),
    oauth_service: IOAuthService = Depends(get_yandex_oauth_service),
    use_case: LoginCourierWithOAuthUseCase = Depends(
        get_login_courier_use_case
    ),
):
    try:
        user_info = await oauth_service.get_user_info(
            code=code,
            redirect_uri="http://localhost:8000/api/v1/auth/courier/yandex/callback",
        )
    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail=f"Yandex courier auth failed: {exc}",
        )

    return await use_case.execute(user_info)