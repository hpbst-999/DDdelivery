import uuid
from typing import TypedDict, Protocol
from src.identity.domain.entities.OTP import OTP
from src.identity.domain.value_objects.phone_number import PhoneNumber
from src.identity.domain.value_objects.email import Email
from src.identity.domain.entities.account import Account
from src.identity.domain.entities.courier_profile import CourierProfile
from src.identity.domain.entities.user_profile import UserProfile
from datetime import datetime
from src.outbox.application.interfaces import IOutboxRepository
class IOTPRepository(Protocol):
    def save_otp(self, otp: OTP) -> None:
        ...
    def get_otp_by_session(self, session_id: str) -> OTP| None:
        ...
    def get_latest_otp_by_phone(self, phone: PhoneNumber) -> OTP| None: 
        ...
    def update_otp(self, otp: OTP) -> None: 
        ...

class ISmsSender(Protocol):
    def send_sms(self, phone: PhoneNumber, text: str) -> None: 
        ...

class IEmailSender(Protocol):
    def send_email(self, email: Email, text: str) -> None: 
        ...

class IRefreshTokenRepository(Protocol):
    def save_refresh_token(self, id: uuid.UUID, account_id: uuid.UUID, refresh_token: str, expires_at: datetime, created_at: datetime, is_revoked: bool) -> None:
        ...
    def get_data_by_token(self, refresh_token: str) -> dict | None:
        ...
    def revoke_token(self, session_id: str) -> None:
        ...

class TokenPair(TypedDict):
    access_token: str
    refresh_token: str

class ITokenService(Protocol):
    def generate_pair(self, account_id: str) -> TokenPair:
        ...
    def validate_access_token(self, token: str) -> dict:
        ...
    def validate_refresh_token(self, token: str) -> dict:
        ...

class IAccountRepository(Protocol):
    def get_account_by_id(self, account_id: uuid.UUID) -> Account | None:
        ...
    def get_account_by_phone(self, phone_number: PhoneNumber) -> Account | None:
        ...
    def get_account_by_email(self, email: Email) -> Account | None:
        ...
    def add_account(self, account: Account) -> None:
        ...
    def update_account(self, account: Account) -> None:
        ...
    def delete_account(self, account_id: uuid.UUID) -> None:
        ...

class IUserProfileRepository(Protocol):
    def get_user_by_id(self, profile_id: uuid.UUID) -> UserProfile | None:
        ...
    def add_user(self, profile: UserProfile) -> None:
        ...
    def update_user(self, profile: UserProfile) -> None:
        ...
    def delete_user(self, profile_id: uuid.UUID) -> None:
        ...

class ICourierProfileRepository(Protocol):
    def get_courier_by_id(self, profile_id: uuid.UUID) -> CourierProfile | None:
        ...
    def add_courier(self, profile: CourierProfile) -> None:
        ...
    def update_courier(self, profile: CourierProfile) -> None:
        ...
    def delete_courier(self, profile_id: uuid.UUID) ->  None:
        ...

class IUnitOfWork(Protocol):
    otp_repository: IOTPRepository
    session_repository: IRefreshTokenRepository
    accounts: IAccountRepository
    user_profiles: IUserProfileRepository
    courier_profiles: ICourierProfileRepository
    #outbox
    outbox: IOutboxRepository

    def __enter__(self):
        ...
    def __exit__(self, exc_type, exc_val, exc_tb):
        ...
    def commit(self):
        ...
    def rollback(self):
        ...



