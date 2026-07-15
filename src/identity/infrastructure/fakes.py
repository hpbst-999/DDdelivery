from typing import Dict, Optional
from src.identity.domain.entities import OTP
from src.identity.domain.value_objects import PhoneNumber
from src.identity.application.interfaces import IOTPRepository, ISmsSender, IUnitOfWork, ISessionRepository
import uuid
from src.identity.domain.entities import Account, UserProfile, CourierProfile
from src.identity.application.interfaces import (
    IAccountRepository, IUserProfileRepository, 
    ICourierProfileRepository, ITokenService
)

class InMemoryOTPRepository(IOTPRepository):
    def __init__(self):
        self._store: Dict[str, OTP] = {}

    def save(self, otp: OTP) -> None:
        self._store[otp.session_id] = otp
        print(f"[БД] Сохранен OTP ({otp.code}) для сессии: {otp.session_id}")

    def get_by_session(self, session_id: str) -> Optional[OTP]:
        return self._store.get(session_id)
    
    def delete_by_session(self, session_id: str) -> None:
        if session_id in self._store:
            del self._store[session_id]
            print(f"[БД] OTP удален по ID сессии: {session_id}")

    def delete_by_phone(self, phone: PhoneNumber) -> None:
        sessions_to_delete = [
            sid for sid, otp in self._store.items() 
            if otp.phone_number.value == phone.value
        ]
        for sid in sessions_to_delete:
            del self._store[sid]
        
        if sessions_to_delete:
            print(f"[БД] Старые OTP удалены для номера {phone.value}")


class FakeSmsSender(ISmsSender):
    def send_sms(self, phone: PhoneNumber, text: str) -> None:
        print(f"[СМС-Шлюз] Сообщение на {phone.value}: {text}")


class FakeUnitOfWork(IUnitOfWork):
    def __init__(self):
        # Существующие
        self.otp_repository = InMemoryOTPRepository()
        self.session_repository = FakeSessionRepository()
        
        # Добавленные
        self.accounts = InMemoryAccountRepository()
        self.user_profiles = InMemoryUserProfileRepository()
        self.courier_profiles = InMemoryCourierProfileRepository()

    def __enter__(self):
        print("[Транзакция] Открыта")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.rollback()
        print("[Транзакция] Закрыта\n")

    def commit(self):
        print("[Транзакция] COMMIT (данные зафиксированы)")

    def rollback(self):
        print("[Транзакция] ROLLBACK (ошибка, откат данных)")

class FakeSessionRepository(ISessionRepository):
    def __init__(self):
        self._store = {} 

    def save_refresh_token(self, session_id: str, account_id: str, refresh_token: str, expires_days: int) -> None:
        self._store[session_id] = {
            "session_id": session_id,
            "account_id": account_id,
            "token": refresh_token
        }

    def get_by_token(self, refresh_token: str) -> dict | None:
        # Проходим по всем сессиям и ищем совпадение
        for session_id, data in self._store.items():
            if data["token"] == refresh_token:
                return data
        return None

    def delete_session(self, session_id: str) -> None:
        self._store.pop(session_id, None)

class InMemoryAccountRepository(IAccountRepository):
    def __init__(self):
        self._store: Dict[str, Account] = {}

    def add_account(self, account: Account) -> None:
        self._store[str(account.id)] = account

    def get_account_by_id(self, account_id: str | uuid.UUID) -> Optional[Account]:
        return self._store.get(str(account_id))

    def get_account_by_phone(self, phone: PhoneNumber) -> Optional[Account]:
        for account in self._store.values():
            if account.phone_number.value == phone.value:
                return account
        return None

    def update_account(self, account: Account) -> None:
        self._store[str(account.id)] = account

    def delete_account(self, account_id: str | uuid.UUID) -> None:
        self._store.pop(str(account_id), None)


class InMemoryUserProfileRepository(IUserProfileRepository):
    def __init__(self):
        self._store: Dict[str, UserProfile] = {}

    def add_user(self, profile: UserProfile) -> None:
        self._store[str(profile.id)] = profile

    def get_user_by_id(self, account_id: str | uuid.UUID) -> Optional[UserProfile]:
        return self._store.get(str(account_id))

    def update_user(self, profile: UserProfile) -> None:
        self._store[str(profile.id)] = profile

    def delete_user(self, account_id: str | uuid.UUID) -> None:
        self._store.pop(str(account_id), None)


class InMemoryCourierProfileRepository(ICourierProfileRepository):
    def __init__(self):
        self._store: Dict[str, CourierProfile] = {}

    def add_courier(self, profile: CourierProfile) -> None:
        self._store[str(profile.id)] = profile

    def get_courier_by_id(self, account_id: str | uuid.UUID) -> Optional[CourierProfile]:
        return self._store.get(str(account_id))

    def update_courier(self, profile: CourierProfile) -> None:
        self._store[str(profile.id)] = profile

    def delete_courier(self, account_id: str | uuid.UUID) -> None:
        self._store.pop(str(account_id), None)


class FakeTokenService(ITokenService):
    def generate_pair(self, account_id: str) -> dict:
        return {
            "access_token": f"fake_access_{account_id}_{uuid.uuid4().hex[:6]}",
            "refresh_token": f"fake_refresh_{account_id}_{uuid.uuid4().hex[:6]}"
        }

    def validate_refresh_token(self, token: str) -> None:
        if not token.startswith("fake_refresh_"):
            raise ValueError("Invalid fake token")