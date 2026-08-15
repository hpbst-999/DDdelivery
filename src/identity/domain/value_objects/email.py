import re
from dataclasses import dataclass
from src.identity.domain.exceptions import InvalidEmailError
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
    
