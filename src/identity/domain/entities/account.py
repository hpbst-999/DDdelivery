import uuid
from typing import  List

from src.identity.domain.value_objects.phone_number import PhoneNumber
from src.identity.domain.value_objects.email import Email
from src.identity.domain.value_objects.enums import AccountRole


class Account:
    def __init__(
        self, 
        id: uuid.UUID, 
        roles: List[AccountRole], 
        phone_number: PhoneNumber | None  = None, 
        email: Email | None = None
    ):
        self.id = id
        self.roles = roles
        self.phone_number = phone_number
        self.email = email

    def add_role(self, role: AccountRole) -> None:
        if role not in self.roles:
            self.roles.append(role)
    
    def remove_role(self, role: AccountRole) -> None:
        if role in self.roles:
            self.roles.remove(role)

    def has_role(self, role: AccountRole) -> bool:
        return role in self.roles

    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "email": self.email,
            "roles": [role.value for role in self.roles]
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Account":
        raw_email = data.get("email")
        email_obj = Email(raw_email) if raw_email else None
        return cls(
            id=uuid.UUID(data["id"]),
            email=email_obj,
            roles=[AccountRole(role) for role in data["roles"]]
        )