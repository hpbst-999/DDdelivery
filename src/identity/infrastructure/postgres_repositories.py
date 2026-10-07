import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.identity.domain.entities.account import Account
from src.identity.domain.entities.OTP import OTP
from src.identity.domain.entities.refresh_token import RefreshToken
from src.identity.domain.entities.user_profile import UserProfile
from src.identity.domain.value_objects.email import Email
from src.identity.domain.value_objects.phone_number import PhoneNumber
from src.identity.infrastructure.models import (
    AccountModel,
    OTPModel,
    RefreshTokenModel,
    UserProfileModel,
)


class SQLAlchemyAccountRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    def _to_entity(self, model: AccountModel) -> Account:
        return Account(
            id=model.id,
            phone_number=PhoneNumber(model.phone_number) if model.phone_number else None,
            email=Email(model.email) if model.email else None,
        )

    async def get_account_by_id(self, id: uuid.UUID) -> Account | None:
        stmt = select(AccountModel).where(AccountModel.id == id)
        result = await self.session.scalars(stmt)
        model = result.one_or_none()

        if not model:
            return None

        return self._to_entity(model)

    async def get_account_by_phone(self, phone_number: PhoneNumber) -> Account | None:
        stmt = select(AccountModel).where(AccountModel.phone_number == phone_number)
        result = await self.session.scalars(stmt)
        model = result.one_or_none()

        if not model:
            return None

        return self._to_entity(model)

    async def get_account_by_email(self, email: Email) -> Account | None:
        stmt = select(AccountModel).where(AccountModel.email == email)
        result = await self.session.scalars(stmt)
        model = result.one_or_none()

        if not model:
            return None

        return self._to_entity(model)

    async def add_account(self, account: Account) -> None:
        model = AccountModel(
            id=account.id,
            phone_number=account.phone_number if account.phone_number else None,
            email=account.email if account.email else None,
        )
        self.session.add(model)
        await self.session.flush()

    async def update_account(self, account: Account) -> None:
        stmt = select(AccountModel).where(AccountModel.id == account.id)
        result = await self.session.scalars(stmt)
        model = result.one_or_none()

        if model:
            model.phone_number = account.phone_number if account.phone_number else None
            model.email = account.email if account.email else None

    async def delete_account(self, id: uuid.UUID) -> None:
        stmt = select(AccountModel).where(AccountModel.id == id)
        result = await self.session.scalars(stmt)
        model = result.one_or_none()

        if model:
            await self.session.delete(model)
            await self.session.flush()


class SQLAlchemyUserProfileRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    def _to_entity(self, model: UserProfileModel) -> UserProfile:
        return UserProfile(
            id=model.id, account_id=model.account_id, name=model.name, address=model.address
        )

    async def get_user_by_id(self, id: uuid.UUID) -> UserProfile | None:
        stmt = select(UserProfileModel).where(UserProfileModel.id == id)
        result = await self.session.scalars(stmt)
        model = result.one_or_none()

        if not model:
            return None

        return self._to_entity(model)

    async def get_user_by_account_id(self, id: uuid.UUID) -> UserProfile | None:
        stmt = select(UserProfileModel).where(UserProfileModel.account_id == id)
        result = await self.session.scalars(stmt)
        model = result.one_or_none()

        if not model:
            return None

        return self._to_entity(model)

    async def add_user(self, profile: UserProfile) -> None:
        model = UserProfileModel(
            id=profile.id, account_id=profile.account_id, name=profile.name, address=profile.address
        )
        self.session.add(model)
        await self.session.flush()

    async def update_user(self, profile: UserProfile) -> None:
        stmt = select(UserProfileModel).where(UserProfileModel.id == profile.id)
        result = await self.session.scalars(stmt)
        model = result.one_or_none()

        if model:
            model.name = profile.name
            model.address = profile.address

    async def delete_user(self, id: uuid.UUID) -> None:
        stmt = select(UserProfileModel).where(UserProfileModel.id == id)
        result = await self.session.scalars(stmt)
        model = result.one_or_none()

        if model:
            await self.session.delete(model)
            await self.session.flush()


class SQLAlchemyOTPRepository:
    def __init__(self, session: AsyncSession):
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
            is_used=model.is_used,
        )

    async def save_otp(self, otp: OTP) -> None:
        model = OTPModel(
            session_id=otp.session_id,
            phone_number=otp.phone_number,
            code=otp.code,
            created_at=otp.created_at,
            expires_at=otp.expires_at,
            attempts_count=otp.attempts_count,
            max_attempts=otp.max_attempts,
            is_used=otp.is_used,
        )
        self.session.add(model)
        await self.session.flush()

    async def get_otp_by_session(self, session_id: uuid.UUID) -> OTP | None:
        stmt = select(OTPModel).where(OTPModel.session_id == session_id)
        result = await self.session.scalars(stmt)
        model = result.one_or_none()

        return self._to_entity(model) if model else None

    async def get_latest_otp_by_phone(self, phone: PhoneNumber) -> OTP | None:
        stmt = (
            select(OTPModel)
            .where(OTPModel.phone_number == phone)
            .order_by(OTPModel.created_at.desc())
            .limit(1)
        )
        result = await self.session.scalars(stmt)
        model = result.first()

        return self._to_entity(model) if model else None

    async def update_otp(self, otp: OTP) -> None:
        stmt = select(OTPModel).where(OTPModel.session_id == otp.session_id)
        result = await self.session.scalars(stmt)
        model = result.one_or_none()

        if model:
            model.attempts_count = otp.attempts_count
            model.is_used = otp.is_used


class SQLAlchemyRefreshTokenRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    def _to_entity(self, model: RefreshTokenModel) -> RefreshToken:
        return RefreshToken(
            id=model.id,
            account_id=model.account_id,
            refresh_token=model.refresh_token,
            expires_at=model.expires_at,
            is_revoked=model.is_revoked,
            created_at=model.created_at,
        )

    async def save_refresh_token(self, token: RefreshToken) -> None:
        model = RefreshTokenModel(
            id=token.id,
            account_id=token.account_id,
            refresh_token=token.refresh_token,
            expires_at=token.expires_at,
            is_revoked=token.is_revoked,
            created_at=token.created_at,
        )
        await self.session.merge(model)
        await self.session.flush()

    async def get_refresh_token(self, refresh_token: str) -> RefreshToken | None:
        stmt = select(RefreshTokenModel).where(
            RefreshTokenModel.refresh_token == refresh_token,
            RefreshTokenModel.is_revoked.is_(False),
        )
        result = await self.session.scalars(stmt)
        model = result.first()
        return self._to_entity(model) if model else None
