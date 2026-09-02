import uuid
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import select
from shapely.geometry import Point
from geoalchemy2.shape import from_shape, to_shape
from src.identity.domain.entities.OTP import OTP
from src.identity.domain.entities.account import Account
from src.identity.domain.entities.courier_profile import CourierProfile
from src.identity.domain.entities.user_profile import UserProfile
from src.identity.domain.value_objects.enums import CourierStatus, AccountRole
from src.identity.domain.value_objects.phone_number import PhoneNumber
from src.identity.domain.value_objects.coordinates import Coordinates
from src.identity.domain.value_objects.email import Email
from src.identity.infrastructure.models import AccountModel, UserProfileModel, CourierProfileModel, OTPModel, RefreshTokenModel


class SQLAlchemyAccountRepository:
    def __init__(self, session: Session):
        self.session = session

    def _to_entity(self, model: AccountModel) -> Account:
        return Account(
            id=model.id,
            roles=[AccountRole(r) for r in model.roles],
            phone_number=PhoneNumber(model.phone_number) if model.phone_number else None,
            email=Email(model.email) if model.email else None)

    def get_account_by_id(self, account_id: uuid.UUID) -> Account | None:
        stmt = select(AccountModel).where(AccountModel.id == account_id)
        model = self.session.scalars(stmt).one_or_none()

        if not model:
            return None
            
        return self._to_entity(model)

    def get_account_by_phone(self, phone_number: PhoneNumber) -> Account | None:
        stmt = select(AccountModel).where(AccountModel.phone_number == phone_number)
        model = self.session.scalars(stmt).one_or_none()

        if not model:
            return None
            
        return self._to_entity(model)

    def get_account_by_email(self, email: Email) -> Account | None:
        stmt = select(AccountModel).where(AccountModel.email == email)
        model = self.session.scalars(stmt).one_or_none()
        
        if not model:
            return None
            
        return self._to_entity(model)

    def add_account(self, account: Account) -> None:
        model = AccountModel(
            id=account.id,
            roles=[role.value for role in account.roles],
            phone_number=account.phone_number.value if account.phone_number else None,
            email=account.email.value if account.email else None
        )
        self.session.add(model)

    def update_account(self, account: Account) -> None:
        stmt = select(AccountModel).where(AccountModel.id == account.id)
        model = self.session.scalars(stmt).one_or_none()

        if model:
            model.roles = [role.value for role in account.roles]
            model.phone_number = account.phone_number.value if account.phone_number else None
            model.email = account.email.value if account.email else None

    def delete_account(self, account_id: uuid.UUID) -> None:
        stmt = select(AccountModel).where(AccountModel.id == account_id)
        model = self.session.scalars(stmt).one_or_none()

        if model:
            self.session.delete(model)


class SQLAlchemyUserProfileRepository:
    def __init__(self, session: Session):
        self.session = session

    def _to_entity(self, model: UserProfileModel) -> UserProfile:
        return UserProfile(
            id=model.id,
            name=model.name,
            address=model.address)

    def get_user_by_id(self, profile_id: uuid.UUID) -> UserProfile | None:
        stmt = select(UserProfileModel).where(UserProfileModel.id == profile_id)
        model = self.session.scalars(stmt).one_or_none()

        if not model:
            return None
            
        return self._to_entity(model)

    def add_user(self, profile: UserProfile) -> None:
        model = UserProfileModel(
            id=profile.id, 
            name=profile.name,
            address=profile.address
        )
        self.session.add(model)

    def update_user(self, profile: UserProfile) -> None:
        stmt = select(UserProfileModel).where(UserProfileModel.id == profile.id)
        model = self.session.scalars(stmt).one_or_none()

        if model:
            model.name = profile.name
            model.address = profile.address

    def delete_user(self, profile_id: uuid.UUID) -> None:
        stmt = select(UserProfileModel).where(UserProfileModel.id == profile_id)
        model = self.session.scalars(stmt).one_or_none()

        if model:
            self.session.delete(model)


class SQLAlchemyCourierProfileRepository:
    def __init__(self, session: Session):
        self.session = session

    def _to_entity(self, model: CourierProfileModel, coords: Coordinates) -> CourierProfile:
        return CourierProfile(
            id=model.id,
            name=model.name,
            status=CourierStatus(model.status),
            coordinates=coords
        )

    def get_courier_by_id(self, profile_id: uuid.UUID) -> CourierProfile | None:
        stmt = select(CourierProfileModel).where(CourierProfileModel.id == profile_id)
        model = self.session.scalars(stmt).one_or_none()

        if not model:
            return None
            
        coords = None
        if model.coordinates is not None:
            shapely_point = to_shape(model.coordinates)
            coords = Coordinates(lat=shapely_point.y, lon=shapely_point.x)

        return self._to_entity(model=model, coords=coords)

    def add_courier(self, profile: CourierProfile) -> None:
        db_point = None
        if profile.coordinates:
            pt = Point(profile.coordinates.lon, profile.coordinates.lat)
            db_point = from_shape(pt, srid=4326)

        model = CourierProfileModel(
            id=profile.id,
            name=profile.name,
            status=profile.status.value,
            coordinates=db_point
        )
        self.session.add(model)

    def update_courier(self, profile: CourierProfile) -> None:
        stmt = select(CourierProfileModel).where(CourierProfileModel.id == profile.id)
        model = self.session.scalars(stmt).one_or_none()

        if model:
            model.name = profile.name
            model.status = profile.status.value
            
            if profile.coordinates:
                pt = Point(profile.coordinates.lon, profile.coordinates.lat)
                model.coordinates = from_shape(pt, srid=4326)
            else:
                model.coordinates = None

    def delete_courier(self, profile_id: uuid.UUID) -> None:
        stmt = select(CourierProfileModel).where(CourierProfileModel.id == profile_id)
        model = self.session.scalars(stmt).one_or_none()
        if model:
            self.session.delete(model)

class SQLAlchemyOTPRepository:
    def __init__(self, session: Session):
        self.session = session

    def _to_entity(self, model: OTPModel) -> OTP:
        return OTP(
            session_id=model.session_id,
            phone_number=PhoneNumber(model.phone_number),
            code=model.code,
            created_at=model.created_at,
            expires_at=model.expires_at,
            attempts_count=model.attempts_count,
            max_attempts=model.max_attempts,
            is_used=model.is_used
        )

    def save_otp(self, otp: OTP) -> None:
        model = OTPModel(
            session_id=otp.session_id,
            phone_number=otp.phone_number.value,
            code=otp.code,
            created_at=otp.created_at,
            expires_at=otp.expires_at,
            attempts_count=otp.attempts_count,
            max_attempts=otp.max_attempts,
            is_used=otp.is_used
        )
        self.session.add(model)

    def get_otp_by_session(self, session_id: str) -> OTP | None:
        stmt = select(OTPModel).where(OTPModel.session_id == session_id)
        model = self.session.scalars(stmt).one_or_none()

        return self._to_entity(model) if model else None

    def get_latest_otp_by_phone(self, phone: PhoneNumber) -> OTP | None:
        stmt = select(OTPModel).where(OTPModel.phone_number == phone.value).order_by(OTPModel.created_at.desc()).limit(1)
        model = self.session.scalars(stmt).first()

        return self._to_entity(model) if model else None

    def update_otp(self, otp: OTP) -> None:
        stmt = select(OTPModel).where(OTPModel.session_id == otp.session_id)
        model = self.session.scalars(stmt).one_or_none()

        if model:
            model.attempts_count = otp.attempts_count
            model.is_used = otp.is_used

class SQLAlchemyRefreshTokenRepository:
    def __init__(self, session: Session):
        self.session = session

    def save_refresh_token(self,id: uuid.UUID, account_id: uuid.UUID, refresh_token: str,expires_at: datetime, created_at: datetime) -> None:
        model = RefreshTokenModel(
            id=id,
            account_id=account_id,
            refresh_token=refresh_token,
            expires_at=expires_at,
            created_at=created_at,
            is_revoked=False
        )
        self.session.add(model)

    def get_data_by_token(self, refresh_token: str) -> RefreshTokenModel | None:
        stmt = select(RefreshTokenModel).where(RefreshTokenModel.refresh_token == refresh_token,RefreshTokenModel.is_revoked.is_(False))
        model = self.session.scalars(stmt).first()
        return model

    def revoke_token(self, refresh_token: str) -> None:
        stmt = select(RefreshTokenModel).where(RefreshTokenModel.refresh_token == refresh_token)
        model = self.session.scalars(stmt).first()
        if model:
            model.is_revoked = True