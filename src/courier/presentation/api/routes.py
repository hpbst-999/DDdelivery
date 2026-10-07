from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status

from src.courier.domain.exceptions import ProfileAlreadyExistsError, ProfileNotFoundError
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
from src.identity.presentation.security import get_current_account_id

router = APIRouter(tags=["Courier"])


@router.get("/me", response_model=CourierProfileResponse)
async def get_courier_profile(
    account_id: UUID = Depends(get_current_account_id),
    use_case=Depends(get_courier_profile_use_case),
) -> CourierProfileResponse:
    try:
        profile = await use_case.execute(account_id=account_id)
        return profile
    except ProfileNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)


@router.post("/me", status_code=status.HTTP_201_CREATED)
async def create_courier_profile(
    account_id: UUID = Depends(get_current_account_id),
    use_case=Depends(get_create_courier_use_case),
) -> None:
    try:
        await use_case.execute(account_id=account_id)
    except ProfileAlreadyExistsError:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT)


@router.patch("/me", status_code=status.HTTP_204_NO_CONTENT)
async def update_courier_profile(
    data: UpdateCourierProfileRequest,
    account_id: UUID = Depends(get_current_account_id),
    use_case=Depends(get_update_courier_profile_use_case),
) -> None:
    try:
        await use_case.execute(account_id=account_id, full_name=data.full_name)
    except ProfileNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/me", status_code=204)
async def delete_courier_account(
    account_id: UUID = Depends(get_current_account_id),
    use_case=Depends(get_delete_courier_use_case),
) -> None:
    try:
        await use_case.execute(account_id=account_id)
    except ProfileNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)


@router.patch("/me/status", status_code=status.HTTP_204_NO_CONTENT)
async def change_courier_status(
    target_status: CourierStatus = Query(..., description="Courier status"),
    account_id: UUID = Depends(get_current_account_id),
    use_case=Depends(get_change_courier_status_use_case),
) -> None:
    try:
        await use_case.execute(account_id=account_id, target_status=target_status)
    except ProfileNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
