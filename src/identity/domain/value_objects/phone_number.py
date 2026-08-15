import re
from dataclasses import dataclass
from src.identity.domain.exceptions import InvalidPhoneNumberError

@dataclass(frozen=True)
class PhoneNumber:
    value: str

    def __post_init__(self):
        phone_number = re.sub(r'[\s\-\(\)]', '', self.value)
        if not re.match(r'^(?:\+7|8)\d{10}$', phone_number):
            raise InvalidPhoneNumberError(f"Incorrect phone number format")
        if phone_number.startswith('8'):
            phone_number = '+7' + phone_number[1:] 
        object.__setattr__(self, 'value', phone_number)

    def __str__(self) -> str:
        return self.value