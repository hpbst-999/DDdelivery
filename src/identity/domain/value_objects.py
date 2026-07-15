import re
from dataclasses import dataclass
from src.identity.domain.exceptions import InvalidPhoneNumberError, InvalidEmailError, InvalidCoordinatesError

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

@dataclass(frozen=True)
class Email:
    value: str

    def __post_init__(self):
        clean_email = str(self.value).strip().lower()
        object.__setattr__(self, 'value', clean_email)
        if not re.match(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", self.value):
            raise InvalidEmailError(f"Incorrect email format")

    def __str__(self) -> str:
        return self.value
    
@dataclass(frozen=True)
class Coordinates:
    lon: float 
    lat: float 

    def __post_init__(self):
        if not (-180.0 <= self.lon <= 180.0):
            raise InvalidCoordinatesError("The longitude should be between -180 and 180")
        if not (-90.0 <= self.lat <= 90.0):
            raise InvalidCoordinatesError("The latitude should be between -90 and 90")