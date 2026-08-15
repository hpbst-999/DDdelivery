from pydantic import BaseModel, Field
from src.identity.domain.value_objects.enums import CourierStatus
import uuid
from typing import Optional


class RequestOTP(BaseModel):
    phone: str = Field(..., description="Phone number", json_schema_extra={"example": "8 (999) 123-45-67"})
class ResponseOTP(BaseModel):
    session_id: str


class VerifyOTPRequest(BaseModel):
    session_id: str = Field(..., description="ID session")
    code: str = Field(..., min_length=4, max_length=4, description="SMS code")
class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"


class RefreshRequest(BaseModel):
    refresh_token: str

class LogoutRequest(BaseModel):
    refresh_token: str

class CoordinatesSchema(BaseModel):
    lat: float = Field(..., ge=-90.0, le=90.0, description="Latitude")
    lon: float = Field(..., ge=-180.0, le=180.0, description="Longitude")

class UpdateCourierProfileRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=100, description="Courier name")


class CourierProfileResponse(BaseModel):
    id: uuid.UUID
    name: Optional[str]
    status: CourierStatus
    coordinates: Optional[CoordinatesSchema]


class UpdateUserProfileRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=100, description="User name")
    address: str = Field(..., min_length=5, max_length=255, description="Main delivery address")


class UserProfileResponse(BaseModel):
    id: uuid.UUID
    name: Optional[str]
    address: Optional[str]
