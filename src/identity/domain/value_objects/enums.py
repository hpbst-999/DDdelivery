from enum import Enum

class AccountRole(str, Enum):
    USER = "user"
    COURIER = "courier"

class CourierStatus(str, Enum):
    OFFLINE = "offline"
    ONLINE = "online"
    BUSY = "busy"