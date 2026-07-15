import uuid
from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from src.identity.domain.entities import CourierStatus
from geoalchemy2 import Geometry
from src.core.database import Base


class AccountModel(Base):
    __tablename__ = 'accounts'
    
    id = Column(UUID(as_uuid=True), primary_key=True)
    phone_number = Column(String(20), unique=True, nullable=True)
    email = Column(String(255), unique=True, nullable=True)
    roles = Column(ARRAY(String), nullable=False) 


class UserProfileModel(Base):
    __tablename__ = 'user_profiles'
    
    id = Column(UUID(as_uuid=True), primary_key=True)
    name = Column(String(255), nullable=True)
    address = Column(String(255), nullable=True)



class CourierProfileModel(Base):
    __tablename__ = 'courier_profiles'
    
    id = Column(UUID(as_uuid=True), primary_key=True)
    name = Column(String(255), nullable=True)
    status = Column(
        String(50), 
        default=CourierStatus.OFFLINE.value,
        nullable=False
    )
    coordinates = Column(Geometry(geometry_type='POINT', srid=4326, spatial_index=True), nullable=True)
    