import uuid
from sqlalchemy.orm import Session
from shapely.geometry import Point
from geoalchemy2.shape import from_shape, to_shape
from src.identity.application.interfaces import IAccountRepository, IUserProfileRepository, ICourierProfileRepository
from src.identity.domain.entities import (
    Account, AccountRole, UserProfile, CourierProfile, 
    Coordinates, CourierStatus, PhoneNumber, Email
)
from src.identity.infrastructure.models import AccountModel, UserProfileModel, CourierProfileModel


class SQLAlchemyAccountRepository(IAccountRepository):
    def __init__(self, session: Session):
        self.session = session

    def get_account_by_id(self, account_id: uuid.UUID) -> Account | None:
        model = self.session.query(AccountModel).filter_by(id=account_id).first()
        if not model:
            return None
            
        return Account(
            id=model.id,
            roles=[AccountRole(r) for r in model.roles],
            phone_number=PhoneNumber(model.phone_number) if model.phone_number else None,
            email=Email(model.email) if model.email else None
        )

    def get_account_by_phone(self, phone_number: PhoneNumber) -> Account | None:
        model = self.session.query(AccountModel).filter_by(phone_number=phone_number.value).first()
        if not model:
            return None
            
        return Account(
            id=model.id,
            roles=[AccountRole(r) for r in model.roles],
            phone_number=phone_number,
            email=Email(model.email) if model.email else None
        )

    def get_account_by_email(self, mail: Email) -> Account | None:
        model = self.session.query(AccountModel).filter_by(email=mail.value).first()
        if not model:
            return None
            
        return Account(
            id=model.id,
            roles=[AccountRole(r) for r in model.roles],
            phone_number=PhoneNumber(model.phone_number) if model.phone_number else None,
            email=mail
        )

    def add_account(self, account: Account) -> None:
        model = AccountModel(
            id=account.id,
            roles=[role.value for role in account.roles],
            phone_number=account.phone_number.value if account.phone_number else None,
            email=account.email.value if account.email else None
        )
        self.session.add(model)

    def update_account(self, account: Account) -> None:
        model = self.session.query(AccountModel).filter_by(id=account.id).first()
        if model:
            model.roles = [role.value for role in account.roles]
            model.phone_number = account.phone_number.value if account.phone_number else None
            model.email = account.email.value if account.email else None

    def delete_account(self, account_id: uuid.UUID) -> None:
        model = self.session.query(AccountModel).filter_by(id=account_id).first()
        if model:
            self.session.delete(model)


class SQLAlchemyUserProfileRepository(IUserProfileRepository):
    def __init__(self, session: Session):
        self.session = session

    def get_user_by_id(self, profile_id: uuid.UUID) -> UserProfile | None:
        model = self.session.query(UserProfileModel).filter_by(id=profile_id).first()
        if not model:
            return None
            
        return UserProfile(
            id=model.id,
            name=model.name,
            address=model.address
        )

    def add_user(self, profile: UserProfile) -> None:
        model = UserProfileModel(
            id=profile.id, 
            name=profile.name,
            address=profile.address
        )
        self.session.add(model)

    def update_user(self, profile: UserProfile) -> None:
        model = self.session.query(UserProfileModel).filter_by(id=profile.id).first()
        if model:
            model.name = profile.name
            model.address = profile.address

    def delete_user(self, profile_id: uuid.UUID) -> None:
        model = self.session.query(UserProfileModel).filter_by(id=profile_id).first()
        if model:
            self.session.delete(model)


class SQLAlchemyCourierProfileRepository(ICourierProfileRepository):
    def __init__(self, session: Session):
        self.session = session

    def get_courier_by_id(self, profile_id: uuid.UUID) -> CourierProfile | None:
        model = self.session.query(CourierProfileModel).filter_by(id=profile_id).first()
        if not model:
            return None
            
        coords = None
        if model.coordinates is not None:
            shapely_point = to_shape(model.coordinates)
            coords = Coordinates(lat=shapely_point.y, lon=shapely_point.x)

        return CourierProfile(
            id=model.id,
            name=model.name,
            status=CourierStatus(model.status),
            coordinates=coords
        )

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
        model = self.session.query(CourierProfileModel).filter_by(id=profile.id).first()
        if model:
            model.name = profile.name
            model.status = profile.status.value
            
            if profile.coordinates:
                pt = Point(profile.coordinates.lon, profile.coordinates.lat)
                model.coordinates = from_shape(pt, srid=4326)
            else:
                model.coordinates = None

    def delete_courier(self, profile_id: uuid.UUID) -> None:
        model = self.session.query(CourierProfileModel).filter_by(id=profile_id).first()
        if model:
            self.session.delete(model)