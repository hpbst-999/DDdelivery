import jwt
import uuid
from datetime import datetime, timedelta, timezone
from src.identity.application.interfaces import ITokenService, TokenPair


class JwtTokenService(ITokenService):
    def __init__(self, secret_key: str):
        self.secret_key = secret_key
        self.algorithm = "HS256"

    def generate_pair(self, account_id: uuid.UUID) -> TokenPair:
        now = datetime.now(timezone.utc)
        
        access_payload = {
            "sub": str(account_id),
            "type": "access",
            "exp": now + timedelta(minutes=35)
        }
        access_token = jwt.encode(access_payload, self.secret_key, algorithm=self.algorithm)

        refresh_payload = {
            "sub": str(account_id),
            "type": "refresh",
            "jti": str(uuid.uuid4()), 
            "exp": now + timedelta(days=30)
        }
        refresh_token = jwt.encode(refresh_payload, self.secret_key, algorithm=self.algorithm)

        return {
            "access_token": access_token,
            "refresh_token": refresh_token
        }
    
    def validate_access_token(self, token: str) -> dict:
            try:
                payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
             
                if payload.get("type") != "access":
                    raise ValueError("Invalid token type.")
                return payload
            
            except jwt.ExpiredSignatureError:
                raise ValueError("The Access token has expired.")
            except jwt.InvalidTokenError:
                raise ValueError("Invalid token.")

    def validate_refresh_token(self, token: str) -> dict:
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            
            if payload.get("type") != "refresh":
                raise ValueError("Invalid token type.")
            return payload
            
        except jwt.ExpiredSignatureError:
            raise ValueError("The Refresh token has expired.")
        except jwt.InvalidTokenError:
            raise ValueError("Invalid token.")