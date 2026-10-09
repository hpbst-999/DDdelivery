import uuid
from typing import Any

import pytest

from src.identity.infrastructure.security_jwt import TokenGenerator, TokenValidator


@pytest.fixture
def secret_key() -> str:
    return "test_secret_key_for_jwt_token_signing_12345"


@pytest.fixture
def token_generator(secret_key: str) -> TokenGenerator:
    return TokenGenerator(
        secret_key=secret_key,
        access_token_expire_minutes=15,
        refresh_token_expire_minutes=30,
    )


@pytest.fixture
def token_validator(secret_key: str) -> TokenValidator:
    return TokenValidator(secret_key=secret_key)


def test_generate_pair_round_trips_through_validation(
    token_generator: TokenGenerator,
    token_validator: TokenValidator,
) -> None:
    account_id = uuid.uuid4()

    pair = token_generator.generate_pair(account_id=account_id)

    access_payload = token_validator.validate_access_token(pair.access_token)
    refresh_payload = token_validator.validate_refresh_token(pair.refresh_token)

    assert access_payload["sub"] == str(account_id)
    assert access_payload["type"] == "access"
    assert refresh_payload["sub"] == str(account_id)
    assert refresh_payload["type"] == "refresh"


def test_validate_access_token_rejects_refresh_token(
    token_generator: TokenGenerator,
    token_validator: TokenValidator,
) -> None:
    pair = token_generator.generate_pair(account_id=uuid.uuid4())

    with pytest.raises(ValueError, match="Invalid token type"):
        token_validator.validate_access_token(pair.refresh_token)


def test_validate_rejects_token_signed_with_a_different_secret(
    token_validator: TokenValidator,
) -> None:
    other_generator = TokenGenerator(
        secret_key="completely_different_signing_key_99999",
        access_token_expire_minutes=15,
        refresh_token_expire_minutes=30,
    )
    pair = other_generator.generate_pair(account_id=uuid.uuid4())

    with pytest.raises(ValueError, match="Invalid token signature or payload"):
        token_validator.validate_access_token(pair.access_token)


def test_validate_rejects_garbage_token(token_validator: TokenValidator) -> None:
    with pytest.raises(ValueError, match="Invalid token signature or payload"):
        token_validator.validate_access_token("not-a-jwt")