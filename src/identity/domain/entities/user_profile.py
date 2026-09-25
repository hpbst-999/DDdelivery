import uuid

class UserProfile:
    def __init__(
        self, 
        id: uuid.UUID, 
        account_id: uuid.UUID,
        name: str | None = None, 
        address: str | None = None
    ):
        self.id = id
        self.account_id = account_id
        self.name = name
        self.address = address

    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "account_id": str(self.account_id),
            "name": self.name,
            "address": self.address
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "UserProfile":
        return cls(
            id=uuid.UUID(data["id"]),
            account_id=uuid.UUID(data["account_id"]),
            name=data.get("name"),    
            address=data.get("address")
        )