from dataclasses import dataclass
import uuid
import random
from enum import Enum
from datetime import datetime, timedelta, timezone
from src.identity.domain.value_objects import PhoneNumber, Email, Coordinates

@dataclass
class OTP:
    session_id: str
    phone_number: PhoneNumber
    code: str
    expires_at: datetime

    @classmethod
    def generate_otp(cls, phone: PhoneNumber) -> "OTP":
        return cls(
            session_id=str(uuid.uuid4()),
            phone_number=phone,
            code=str(random.randint(1000, 9999)),
            expires_at=datetime.now(timezone.utc) + timedelta(minutes=5)
        )

    def is_expired(self) -> bool:
        return datetime.now(timezone.utc) > self.expires_at

class AccountRole(str, Enum):
    USER = "user"
    COURIER = "courier"

class CourierStatus(str, Enum):
    OFFLINE = "offline"
    ONLINE = "online"
    BUSY = "busy" 

@dataclass
class Account:
    id: uuid.UUID
    roles: list[AccountRole]
    phone_number: PhoneNumber | None = None
    email: Email | None = None

    def add_role(self, role: AccountRole) -> None:
        if role not in self.roles:
            self.roles.append(role)
    
    def remove_role(self, role: AccountRole) -> None:
        if role in self.roles:
            self.roles.remove(role)

    def has_role(self, role: AccountRole) -> bool:
        return role in self.roles

@dataclass
class UserProfile:
    id: uuid.UUID
    name: str | None = None
    address: str | None = None

@dataclass
class CourierProfile:
    id: uuid.UUID
    name: str | None = None
    status: CourierStatus = CourierStatus.OFFLINE
    coordinates: Coordinates | None = None 

    def update_coordinates(self, lon: float, lat: float) -> None:
        self.coordinates = Coordinates(lon=lon, lat=lat)

    def go_online(self) -> None:
        self.status = CourierStatus.ONLINE

    def go_offline(self) -> None:
        self.status = CourierStatus.OFFLINE
        
    def assign_order(self) -> None:
        self.status = CourierStatus.BUSY