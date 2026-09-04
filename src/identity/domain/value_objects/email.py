import re
from src.identity.domain.exceptions import InvalidEmailError
    
class Email(str):
    def __new__(cls, value: str):
        clean_email = str(value).strip().lower()
        
        if not re.match(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", clean_email):
            raise InvalidEmailError(f"Incorrect email format")
        
        return super().__new__(cls, clean_email)