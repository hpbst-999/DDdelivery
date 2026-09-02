import uuid
from src.identity.domain.value_objects.coordinates import Coordinates
from src.identity.domain.value_objects.enums import CourierStatus

class CourierProfile:
    def __init__(
        self, 
        id: uuid.UUID, 
        name: str| None = None, 
        status: CourierStatus = CourierStatus.OFFLINE, 
        coordinates:  Coordinates | None= None
    ):
        self.id = id
        self.name = name
        self.status = status
        self.coordinates = coordinates

    def update_coordinates(self, lon: float, lat: float) -> None:
        self.coordinates = Coordinates(lon=lon, lat=lat)

    def go_online(self) -> None:
        self.status = CourierStatus.ONLINE

    def go_offline(self) -> None:
        self.status = CourierStatus.OFFLINE
        
    def assign_order(self) -> None:
        self.status = CourierStatus.BUSY
