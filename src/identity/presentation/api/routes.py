from fastapi import APIRouter, Depends, HTTPException
from src.identity.domain.exceptions import DomainException
from src.identity.domain.entities.account import Account
from src.identity.domain.entities.user_profile import UserProfile
from src.identity.domain.entities.courier_profile import CourierProfile
from src.identity.presentation.api.schemas import RequestOTP,UpdateUserProfileRequest,UpdateCourierProfileRequest ,ResponseOTP,CourierProfileResponse, UserProfileResponse, VerifyOTPRequest, TokenResponse, RefreshRequest, LogoutRequest
from src.identity.application.use_cases.request_otp import RequestOTPUseCase
from src.identity.application.use_cases.refresh_session import RefreshSessionUseCase
from src.identity.application.use_cases.logout import LogoutUseCase
from src.identity.presentation.dependencies import (
    get_request_otp_use_case,
    get_verify_user_otp_use_case,
    get_verify_courier_otp_use_case,
    get_refresh_session_use_case,
    get_logout_use_case,
    get_courier_profile_use_case,
    get_user_profile_use_case,
    get_update_user_profile_use_case,
    get_update_courier_profile_use_case,
    get_delete_user_use_case,
    get_delete_courier_use_case,
    get_current_account
)

router = APIRouter(tags=["Authentication"])

@router.post("/otp/request", response_model=ResponseOTP)
def send_code(
    request: RequestOTP,
    use_case: RequestOTPUseCase = Depends(get_request_otp_use_case)
):
    try:
        session_id = use_case.execute(raw_phone_number=request.phone)
        return ResponseOTP(session_id=str(session_id))
    
    except DomainException as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@router.post("/verify/user", response_model=TokenResponse)
def verify_user_otp(
    request: VerifyOTPRequest,
    use_case = Depends(get_verify_user_otp_use_case)
):
    try:
        tokens = use_case.execute(session_id=request.session_id, input_code=request.code)
        return TokenResponse(
            access_token=tokens["access_token"],
            refresh_token=tokens["refresh_token"]
        )
    
    except DomainException as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@router.post("/verify/courier", response_model=TokenResponse)
def verify_courier_otp(
    request: VerifyOTPRequest,
    use_case = Depends(get_verify_courier_otp_use_case)
):
    try:
        tokens = use_case.execute(session_id=request.session_id, input_code=request.code)
        return TokenResponse(
            access_token=tokens["access_token"],
            refresh_token=tokens["refresh_token"]
        )
    
    except DomainException as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@router.post("/refresh", response_model=TokenResponse)
def refresh_token(
    request: RefreshRequest,
    use_case: RefreshSessionUseCase = Depends(get_refresh_session_use_case)
):
    try:
        tokens = use_case.execute(raw_refresh_token=request.refresh_token)
        
        return TokenResponse(
            access_token=tokens["access_token"],
            refresh_token=tokens["refresh_token"]
        )
    except DomainException as e:
        raise HTTPException(status_code=401, detail=str(e))
    

@router.post("/logout")
def logout(
    request: LogoutRequest,
    use_case: LogoutUseCase = Depends(get_logout_use_case)
):
    try:
        use_case.execute(raw_refresh_token=request.refresh_token)
    except DomainException:
        pass
    
    return {"message": "successful logout"}



@router.get("/users/me", response_model=UserProfileResponse)
def get_user_profile(
    account: Account = Depends(get_current_account),
    use_case = Depends(get_user_profile_use_case)
):
    try:
        profile = use_case.execute(profile_id=account.id)
        return profile
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception :
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.patch("/users/me", response_model=UserProfileResponse)
def update_user_profile(
    data: UpdateUserProfileRequest,
    account: Account = Depends(get_current_account),
    use_case = Depends(get_update_user_profile_use_case)
):
    try:
        profile = use_case.execute(
            account_id=account.id, 
            name=data.name, 
            address=data.address
        )
        return profile
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception :
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.delete("/users/me", status_code=204)
def delete_user_account(
    account: Account = Depends(get_current_account),
    use_case = Depends(get_delete_user_use_case)
):
    try:
        use_case.execute(account_id=account.id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="Internal Server Error")
    
@router.get("/couriers/me", response_model=CourierProfileResponse)
def get_courier_profile(
    account: Account = Depends(get_current_account),
    use_case = Depends(get_courier_profile_use_case)
):
    try:
        profile = use_case.execute(account_id=account.id)
        return profile
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="Internal Server Error")
    
@router.patch("/couriers/me", response_model=CourierProfileResponse)
def update_courier_profile(
    data: UpdateCourierProfileRequest,
    account: Account = Depends(get_current_account),
    use_case = Depends(get_update_courier_profile_use_case)
):
    try:
        profile = use_case.execute(account_id=account.id, name=data.name)
        return profile
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500,detail="Internal Server Error")


@router.delete("/couriers/me", status_code=204)
def delete_courier_account(
    account: Account = Depends(get_current_account),
    use_case = Depends(get_delete_courier_use_case)
):
    try:
        use_case.execute(account_id=account.id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="Internal Server Error")