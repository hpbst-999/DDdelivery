import re
from src.identity.domain.exceptions import InvalidPhoneNumberError

class PhoneNumber(str):
    def __new__(cls, value: str):
        phone_number = re.sub(r'[\s\-\(\)]', '', str(value))
        
        if not re.match(r'^(?:\+7|8)\d{10}$', phone_number):
            raise InvalidPhoneNumberError(f"Incorrect phone number format")
        
        if phone_number.startswith('8'):
            phone_number = '+7' + phone_number[1:]
        
        return super().__new__(cls, phone_number)