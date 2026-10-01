import uuid

from src.identity.domain.entities.account import Account
from src.identity.domain.entities.OTP import OTP
from src.identity.domain.entities.user_profile import UserProfile
from src.outbox.domain.outbox_message import OutboxMessage


class FakeOTPRepository:
    def __init__(self):
        self._storage: dict[str, list[OTP]] = {}

    async def get_latest_otp_by_phone(self, phone) -> OTP | None:
        otps = self._storage.get(str(phone), [])
        if not otps:
            return None
        return otps[-1]

    async def get_otp_by_session(self, session_id: uuid.UUID) -> OTP | None:
        for otps in self._storage.values():
            for otp in otps:
                if otp.session_id == session_id:
                    return otp
        return None

    async def update_otp(self, otp: OTP) -> None:
        pass

    async def save_otp(self, otp: OTP) -> None:
        phone_str = str(otp.phone_number)
        if phone_str not in self._storage:
            self._storage[phone_str] = []
        self._storage[phone_str].append(otp)


class FakeOutboxRepository:
    def __init__(self):
        self.messages: list[OutboxMessage] = []

    async def add(self, message: OutboxMessage) -> None:
        self.messages.append(message)


class FakeAccountRepository:
    def __init__(self):
        self.accounts: dict[uuid.UUID, Account] = {}

    async def get_account_by_phone(self, phone) -> Account | None:
        for account in self.accounts.values():
            if str(account.phone_number) == str(phone):
                return account
        return None

    async def get_account_by_email(self, email) -> Account | None:
        for account in self.accounts.values():
            if hasattr(account, "email") and str(account.email) == str(email):
                return account
        return None

    async def add_account(self, account: Account) -> None:
        self.accounts[account.id] = account

    async def get_account_by_id(self, account_id: uuid.UUID) -> Account | None:
        return self.accounts.get(account_id)

    async def delete_account(self, account_id: uuid.UUID) -> None:
        self.accounts.pop(account_id, None)


class FakeUserProfileRepository:
    def __init__(self):
        self.profiles: dict[uuid.UUID, UserProfile] = {}

    async def add_user(self, user_profile: UserProfile) -> None:
        self.profiles[user_profile.id] = user_profile

    async def get_user_by_id(self, profile_id: uuid.UUID) -> UserProfile | None:
        return self.profiles.get(profile_id)

    async def update_user(self, profile: UserProfile) -> None:
        self.profiles[profile.id] = profile

    async def delete_user(self, account_id: uuid.UUID) -> None:
        profile_id_to_delete = None
        for pid, profile in self.profiles.items():
            if profile.account_id == account_id:
                profile_id_to_delete = pid
                break

        if profile_id_to_delete:
            self.profiles.pop(profile_id_to_delete)


class FakeRefreshTokenRepository:
    def __init__(self):
        self.tokens: dict[uuid.UUID, dict] = {}

    async def save_refresh_token(
        self, id, account_id, refresh_token, expires_at, created_at
    ) -> None:
        self.tokens[id] = {
            "account_id": account_id,
            "refresh_token": refresh_token,
            "expires_at": expires_at,
            "created_at": created_at,
        }

    async def revoke_token(self, refresh_token: str) -> None:
        token_id_to_delete = None
        for tid, tdata in self.tokens.items():
            if tdata["refresh_token"] == refresh_token:
                token_id_to_delete = tid
                break

        if token_id_to_delete:
            self.tokens.pop(token_id_to_delete)

    async def get_data_by_token(self, refresh_token: str):
        for tdata in self.tokens.values():
            if tdata["refresh_token"] == refresh_token:

                class SessionDataDTO:
                    def __init__(self, data):
                        self.account_id = data["account_id"]
                        self.expires_at = data["expires_at"]

                return SessionDataDTO(tdata)
        return None


class FakeCacheRepository:
    def __init__(self):
        self._cache: dict[str, dict] = {}

    async def get(self, key: str) -> dict | None:
        return self._cache.get(key)

    async def set(self, key: str, value: dict, ttl_second: int = 600) -> None:
        self._cache[key] = value

    async def delete(self, key: str) -> None:
        self._cache.pop(key, None)


class FakeUnitOfWork:
    def __init__(self):
        self.otp = FakeOTPRepository()
        self.outbox = FakeOutboxRepository()
        self.accounts = FakeAccountRepository()
        self.user_profiles = FakeUserProfileRepository()
        self.refresh_tokens = FakeRefreshTokenRepository()
        self.committed = False
        self.rolled_back = False

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.rolled_back = True

    async def commit(self):
        self.committed = True
