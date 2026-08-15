import uuid
from typing import Optional

class UserProfile:
    def __init__(
        self, 
        id: uuid.UUID, 
        name: Optional[str] = None, 
        address: Optional[str] = None
    ):
        self.id = id
        self.name = name
        self.address = address