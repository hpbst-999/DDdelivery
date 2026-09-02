import uuid

class UserProfile:
    def __init__(
        self, 
        id: uuid.UUID, 
        name: str | None = None, 
        address: str | None = None
    ):
        self.id = id
        self.name = name
        self.address = address