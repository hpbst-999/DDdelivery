import json
import redis
from typing import Optional
from datetime import datetime, timezone
from src.identity.application.interfaces import ISessionRepository, IOTPRepository
from src.identity.domain.entities import OTP
from src.identity.domain.value_objects import PhoneNumber

class RedisSessionRepository(ISessionRepository):
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client

    def save_refresh_token(self, session_id: str, account_id: str, refresh_token: str, expires_days: int) -> None:
        data = {
            "session_id": session_id,
            "account_id": account_id,
            "token": refresh_token
        }
        ttl_seconds = expires_days * 24 * 60 * 60 
        
        with self.redis.pipeline() as pipe:
            pipe.redis.setex(f"session:{session_id}", ttl_seconds, json.dumps(data))
            pipe.redis.setex(f"token_index:{refresh_token}", ttl_seconds, session_id)
            pipe.execute()

    def get_data_by_token(self, refresh_token: str) -> dict | None:
        session_id_bytes = self.redis.get(f"token_index:{refresh_token}")
        if not session_id_bytes:
            return None
            
        session_id = session_id_bytes.decode('utf-8')
        
        data_bytes = self.redis.get(f"session:{session_id}")
        if not data_bytes:
            return None
            
        return json.loads(data_bytes)

    def delete_session(self, session_id: str) -> None:
        data_bytes = self.redis.get(f"session:{session_id}")
        if not data_bytes:
            return
        
        data = json.loads(data_bytes)
        with self.redis.pipeline() as pipe:
            self.redis.delete(f"token_index:{data['token']}")   
            self.redis.delete(f"session:{session_id}")
            pipe.execute() 


class RedisOTPRepository(IOTPRepository):
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client

    def save_otp(self, otp: OTP) -> None:
        ttl = int((otp.expires_at - datetime.now(timezone.utc)).total_seconds())
        if ttl <= 0:
            return 

        data = {
            "session_id": otp.session_id,
            "phone": otp.phone_number.value,
            "code": otp.code,
            "expires_at": otp.expires_at.isoformat()
        }
        with self.redis.pipeline() as pipe:
            self.redis.setex(f"otp:{otp.session_id}", ttl, json.dumps(data))
            self.redis.setex(f"otp_phone:{otp.phone_number.value}", ttl, otp.session_id)
            pipe.execute()

    def get_otp_by_session(self, session_id: str) -> Optional[OTP]:
        data_bytes = self.redis.get(f"otp:{session_id}")
        if not data_bytes:
            return None
            
        data = json.loads(data_bytes)
        
        return OTP(
            session_id=data["session_id"],
            phone_number=PhoneNumber(data["phone"]),
            code=data["code"],
            expires_at=datetime.fromisoformat(data["expires_at"])
        )

    def delete_otp_by_session(self, session_id: str) -> None:
        data_bytes = self.redis.get(f"otp:{session_id}")
        if not data_bytes:
            return
        data = json.loads(data_bytes)
        with self.redis.pipeline() as pipe:
            self.redis.delete(f"otp_phone:{data['phone']}")
            self.redis.delete(f"otp:{session_id}")
            pipe.execute()

    def delete_otp_by_phone(self, phone: PhoneNumber) -> None:
        session_id_bytes = self.redis.get(f"otp_phone:{phone.value}")
        if session_id_bytes:
            session_id = session_id_bytes.decode('utf-8')
            with self.redis.pipeline() as pipe:
                self.redis.delete(f"otp:{session_id}")
                self.redis.delete(f"otp_phone:{phone.value}")
                pipe.execute()