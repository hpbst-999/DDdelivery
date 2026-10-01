import uuid
from datetime import UTC, datetime, timedelta
from typing import Any

import jwt

from src.identity.application.dtos.token_pair import TokenPair


class JwtTokenService:
    def __init__(self, secret_key: str):
        self.secret_key = secret_key
        self.algorithm = "HS256"

    def generate_pair(self, account_id: uuid.UUID) -> TokenPair:
        now = datetime.now(UTC)

        access_payload = {
            "sub": str(account_id),
            "type": "access",
            "iat": now,
            "exp": now + timedelta(minutes=35),
        }
        access_token = jwt.encode(access_payload, self.secret_key, algorithm=self.algorithm)

        refresh_payload = {
            "sub": str(account_id),
            "type": "refresh",
            "jti": str(uuid.uuid4()),
            "iat": now,
            "exp": now + timedelta(days=30),
        }
        refresh_token = jwt.encode(refresh_payload, self.secret_key, algorithm=self.algorithm)

        return TokenPair(access_token=access_token, refresh_token=refresh_token)

    def validate_access_token(self, token: str) -> dict[str, Any]:
        return self._validate_token(token, expected_type="access")

    def validate_refresh_token(self, token: str) -> dict[str, Any]:
        return self._validate_token(token, expected_type="refresh")

    def _validate_token(self, token: str, expected_type: str) -> dict[str, Any]:
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])

            if payload.get("type") != expected_type:
                raise ValueError(f"Invalid token type. Expected {expected_type}.")

            return payload

        except jwt.ExpiredSignatureError as exc:
            raise ValueError("Token has expired.") from exc

        except jwt.InvalidTokenError as exc:
            raise ValueError("Invalid token signature or payload.") from exc
