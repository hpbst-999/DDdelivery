from sqlalchemy import Column, String, Integer, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from src.identity.domain.value_objects.enums import CourierStatus
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

class OTPModel(Base):
    __tablename__ = "otps"

    session_id = Column(String(36), primary_key=True)
    phone_number = Column(String(20), index=True, nullable=False)
    code = Column(String(10), nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    attempts_count = Column(Integer, default=0, nullable=False)
    max_attempts = Column(Integer, default=3, nullable=False)
    is_used = Column(Boolean, default=False, nullable=False)

class RefreshTokenModel(Base):
    __tablename__ = "refresh_tokens"

    id = Column(UUID(as_uuid=True), primary_key=True)
    account_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    refresh_token = Column(String(512), nullable=False, unique=True, index=True)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    is_revoked = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False)