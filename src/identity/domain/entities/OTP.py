import uuid
import random
from datetime import datetime, timedelta, timezone
from src.identity.domain.value_objects.phone_number import PhoneNumber
from src.identity.domain.exceptions import (
    OTPExpiredError,
    OTPMaxAttemptsExceededError,
    InvalidOTPCodeError
)

class OTP:
    def __init__(self, session_id: uuid.UUID, phone_number: PhoneNumber, code: str, 
                created_at: datetime, expires_at: datetime,attempts_count: int = 0,
                max_attempts: int = 3, is_used: bool = False):
        self.session_id = session_id
        self.phone_number = phone_number
        self.code = code
        self.created_at = created_at
        self.expires_at = expires_at
        self.attempts_count = attempts_count
        self.max_attempts = max_attempts
        self.is_used = is_used
        

    @classmethod
    def generate_otp(cls, phone: PhoneNumber, ttl_min: int = 10, max_attempts = 3) -> "OTP":
        return cls(
            session_id=uuid.uuid4(),
            phone_number=phone,
            code=str(random.randint(1000, 9999)),
            created_at = datetime.now(timezone.utc),
            expires_at=datetime.now(timezone.utc) + timedelta(ttl_min),
            attempts_count = 0,
            max_attempts = max_attempts,
            is_used = False
        )

    def is_expired(self) -> bool:
        return datetime.now(timezone.utc) > self.expires_at

    def can_resend(self, cooldown_seconds: int = 60) -> bool:
        interval = (datetime.now(timezone.utc) - self.created_at).total_seconds()
        return interval >= cooldown_seconds

    def verify(self, input_code: str):
        if self.is_used:
            raise InvalidOTPCodeError("OTP code has already been used.")

        if self.is_expired():
            raise OTPExpiredError("OTP code has expired.")

        if self.attempts_count >= self.max_attempts:
            raise OTPMaxAttemptsExceededError("Maximum OTP attempts exceeded.")

        if self.code != input_code:
            self.attempts_count += 1
            raise InvalidOTPCodeError(f"Invalid code. Attempts left: {self.max_attempts - self.attempts_count}")

        self.is_used = True

        
