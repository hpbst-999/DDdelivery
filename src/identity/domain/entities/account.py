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
