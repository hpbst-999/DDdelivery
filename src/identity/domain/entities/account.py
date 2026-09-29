import uuid

from src.identity.domain.value_objects.phone_number import PhoneNumber
from src.identity.domain.value_objects.email import Email


class Account:
    def __init__(
        self, 
        id: uuid.UUID, 
        phone_number: PhoneNumber | None  = None, 
        email: Email | None = None
    ):
        self.id = id
        self.phone_number = phone_number
        self.email = email

    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "phone_number": self.phone_number if self.phone_number else None,
            "email": self.email,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Account":
        raw_email = data.get("email")
        raw_phone = data.get("phone_number")
        email_obj = Email(raw_email) if raw_email else None
        phone_obj = PhoneNumber(raw_phone) if raw_phone else None
        return cls(
            id=uuid.UUID(data["id"]),
            phone_number=phone_obj,
            email=email_obj,
        )