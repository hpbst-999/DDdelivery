from enum import StrEnum


class CourierStatus(StrEnum):
    OFFLINE = "offline"
    ONLINE = "online"
    BUSY = "busy"
