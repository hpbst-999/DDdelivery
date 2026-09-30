from fastapi import APIRouter, Depends, HTTPException, Query

from src.courier.domain.value_objects.enums import CourierStatus
from src.courier.presentation.api.schemas import (
    CourierProfileResponse,
    UpdateCourierProfileRequest,
)
from src.courier.presentation.dependencies import (
    get_change_courier_status_use_case,
    get_courier_profile_use_case,
    get_create_courier_use_case,
    get_delete_courier_use_case,
    get_update_courier_profile_use_case,
)
from src.identity.presentation.dependencies import get_current_account

router = APIRouter(tags=["Courier"])

@router.get("/courier/me", response_model=CourierProfileResponse)
async def get_courier_profile(
    account = Depends(get_current_account),
    use_case = Depends(get_courier_profile_use_case)
):
    try:
        profile = await use_case.execute(account_id=account.id)
        return profile
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.post("/courier/me", status_code=204)
async def create_courier_profile(
    account = Depends(get_current_account),
    use_case = Depends(get_create_courier_use_case)
):
    try:
        await use_case.execute(account_id=account.id)
        return {"message": "Courier profile created successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.patch("/courier/me", response_model=CourierProfileResponse)
async def update_courier_profile(
    data: UpdateCourierProfileRequest,
    account = Depends(get_current_account),
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
    account = Depends(get_current_account),
    use_case = Depends(get_delete_courier_use_case)
):
    try:
        await use_case.execute(account_id=account.id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.patch("/courier/me/status")
async def change_courier_status(
    target_status: CourierStatus = Query(..., description="Courier status"),
    account = Depends(get_current_account),
    use_case = Depends(get_change_courier_status_use_case)
):
    try:
        await use_case.execute(account_id=account.id, target_status=target_status)
        return {"message": f"Status: {target_status.value}"}

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        raise HTTPException(status_code=5000, detail="Server error")
