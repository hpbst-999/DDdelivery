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
    async def save_otp(self, otp: OTP) -> None:
        ...
    async def get_otp_by_session(self, session_id: str) -> OTP| None:
        ...
    async def get_latest_otp_by_phone(self, phone: PhoneNumber) -> OTP| None: 
        ...
    async def update_otp(self, otp: OTP) -> None: 
        ...

# class ISmsSender(Protocol):
#     def send_sms(self, phone: PhoneNumber, text: str) -> None: 
#         ...

# class IEmailSender(Protocol):
#     def send_email(self, email: Email, text: str) -> None: 
#         ...

class IRefreshTokenRepository(Protocol):
    async def save_refresh_token(self, id: uuid.UUID, account_id: uuid.UUID, refresh_token: str, expires_at: datetime, created_at: datetime, is_revoked: bool) -> None:
        ...
    async def get_data_by_token(self, refresh_token: str) -> dict | None:
        ...
    async def revoke_token(self, refresh_token: str) -> None:
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
    async def get_account_by_id(self, account_id: uuid.UUID) -> Account | None:
        ...
    async def get_account_by_phone(self, phone_number: PhoneNumber) -> Account | None:
        ...
    async def get_account_by_email(self, email: Email) -> Account | None:
        ...
    async def add_account(self, account: Account) -> None:
        ...
    async def update_account(self, account: Account) -> None:
        ...
    async def delete_account(self, account_id: uuid.UUID) -> None:
        ...

class IUserProfileRepository(Protocol):
    async def get_user_by_id(self, profile_id: uuid.UUID) -> UserProfile | None:
        ...
    async def add_user(self, profile: UserProfile) -> None:
        ...
    async def update_user(self, profile: UserProfile) -> None:
        ...
    async def delete_user(self, profile_id: uuid.UUID) -> None:
        ...

class ICourierProfileRepository(Protocol):
    async def get_courier_by_id(self, profile_id: uuid.UUID) -> CourierProfile | None:
        ...
    async def add_courier(self, profile: CourierProfile) -> None:
        ...
    async def update_courier(self, profile: CourierProfile) -> None:
        ...
    async def delete_courier(self, profile_id: uuid.UUID) ->  None:
        ...

class IUnitOfWork(Protocol):
    otp: IOTPRepository
    refresh_tokens: IRefreshTokenRepository
    accounts: IAccountRepository
    user_profiles: IUserProfileRepository
    courier_profiles: ICourierProfileRepository
    #outbox
    outbox: IOutboxRepository

    async def __aenter__(self):
        ...
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        ...
    async def commit(self):
        ...
    async def rollback(self):
        ...



