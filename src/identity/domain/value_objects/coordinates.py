from dataclasses import dataclass
from src.identity.domain.exceptions import InvalidCoordinatesError

@dataclass(frozen=True)
class Coordinates:
    lon: float 
    lat: float 

    def __post_init__(self):
        if not (-180.0 <= self.lon <= 180.0):
            raise InvalidCoordinatesError("The longitude should be between -180 and 180")
        if not (-90.0 <= self.lat <= 90.0):
            raise InvalidCoordinatesError("The latitude should be between -90 and 90")