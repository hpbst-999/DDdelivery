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

    def to_dict(self) -> dict:
        return {
            "id": self.str(self.id),
            "name": self.name,
            "address": self.address
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "UserProfile":
        return cls(
            id=uuid.UUID(data["id"]),
            name=data.get("name"),    
            address=data.get("address")
        )