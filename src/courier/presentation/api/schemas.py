import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from src.courier.domain.value_objects.enums import CourierStatus


class UpdateCourierProfileRequest(BaseModel):
    full_name: str | None = Field(
        default=None,
        min_length=2,
        max_length=255,
        description="Full name courier")
    inn: str | None = Field(
        default=None,
        pattern=r"^\d{12}$",
        description="INN")


class CourierProfileResponse(BaseModel):
    id: uuid.UUID
    account_id: uuid.UUID
    full_name: str | None = None
    inn: str | None = None
    is_verified: bool
    verified_at: datetime | None = None
    status: CourierStatus
