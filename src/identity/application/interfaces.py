from abc import ABC, abstractmethod
import uuid
from typing import Optional, TypedDict
from src.identity.domain.entities import OTP
from src.identity.domain.value_objects import PhoneNumber, Email
from src.identity.domain.entities import Account, CourierProfile, UserProfile

class IOTPRepository(ABC):
    @abstractmethod
    def save_otp(self, otp: OTP) -> None:
        pass

    @abstractmethod
    def get_otp_by_session(self, session_id: str) -> Optional[OTP]:
        pass

    @abstractmethod
    def delete_otp_by_session(self, session_id: str) -> None:
        pass

    @abstractmethod
    def delete_otp_by_phone(self, phone: PhoneNumber) -> None:
        pass

class ISmsSender(ABC):
    @abstractmethod
    def send_sms(self, phone: PhoneNumber, text: str) -> None:
        pass


class ISessionRepository(ABC):
    @abstractmethod
    def save_refresh_token(self, session_id: str, account_id: str, refresh_token: str, expires_days: int) -> None:
        pass

    @abstractmethod
    def get_data_by_token(self, refresh_token: str) -> dict | None:
        pass

    @abstractmethod
    def delete_session(self, session_id: str) -> None:
        pass


class TokenPair(TypedDict):
    access_token: str
    refresh_token: str


class ITokenService(ABC):
    @abstractmethod
    def generate_pair(self, account_id: str) -> TokenPair:
        pass

    @abstractmethod
    def validate_access_token(self, token: str) -> dict:
        pass

    @abstractmethod
    def validate_refresh_token(self, token: str) -> dict:
        pass


class IAccountRepository(ABC):
    @abstractmethod
    def get_account_by_id(self, account_id: uuid.UUID) -> Account | None:
        pass

    @abstractmethod
    def get_account_by_phone(self, phone_number: PhoneNumber) -> Account | None:
        pass

    @abstractmethod
    def get_account_by_email(self, mail: Email) -> Account | None:
        pass

    @abstractmethod
    def add_account(self, account: Account) -> None:
        pass

    @abstractmethod
    def update_account(self, account: Account) -> None:
        pass

    @abstractmethod
    def delete_account(self, account_id: uuid.UUID) -> None:
        pass


class IUserProfileRepository(ABC):
    @abstractmethod
    def get_user_by_id(self, profile_id: uuid.UUID) -> UserProfile | None:
        pass

    @abstractmethod
    def add_user(self, profile: UserProfile) -> None:
        pass

    @abstractmethod
    def update_user(self, profile: UserProfile) -> None:
        pass

    @abstractmethod
    def delete_user(self, profile_id: uuid.UUID) -> None:
        pass


class ICourierProfileRepository(ABC):
    @abstractmethod
    def get_courier_by_id(self, profile_id: uuid.UUID) -> CourierProfile | None:
        pass

    @abstractmethod
    def add_courier(self, profile: CourierProfile) -> None:
        pass

    @abstractmethod
    def update_courier(self, profile: CourierProfile) -> None:
        pass

    @abstractmethod
    def delete_courier(self, profile_id: uuid.UUID) ->  None:
        pass


class IOtpService(ABC):
    @abstractmethod
    def send_code(self, phone_number: str) -> None:
        pass

    @abstractmethod
    def verify_otp(self, phone_number: str, code: str) -> bool:
        pass


class IUnitOfWork(ABC):
    otp_repository: IOTPRepository
    session_repository: ISessionRepository
    accounts: IAccountRepository
    user_profiles: IUserProfileRepository
    courier_profiles: ICourierProfileRepository

    @abstractmethod
    def __enter__(self):
        pass

    @abstractmethod
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    @abstractmethod
    def commit(self):
        pass

    @abstractmethod
    def rollback(self):
        pass



