import uuid

import pytest

from src.identity.infrastructure.security_jwt import JwtTokenService


@pytest.mark.asyncio
async def test_generate_pair_round_trips_through_validation(token_service: JwtTokenService):
    account_id = uuid.uuid4()

    pair = token_service.generate_pair(account_id=account_id)

    access_payload = token_service.validate_access_token(pair.access_token)
    refresh_payload = token_service.validate_refresh_token(pair.refresh_token)

    assert access_payload["sub"] == str(account_id)
    assert access_payload["type"] == "access"
    assert refresh_payload["sub"] == str(account_id)
    assert refresh_payload["type"] == "refresh"


@pytest.mark.asyncio
async def test_validate_access_token_rejects_refresh_token(token_service: JwtTokenService):
    pair = token_service.generate_pair(account_id=uuid.uuid4())

    with pytest.raises(ValueError):
        token_service.validate_access_token(pair.refresh_token)


@pytest.mark.asyncio
async def test_validate_rejects_token_signed_with_a_different_secret(
    token_service: JwtTokenService,
):
    other_service = JwtTokenService(secret_key="my_super_secret_test_key_must_be_32_bytes")
    pair = other_service.generate_pair(account_id=uuid.uuid4())

    with pytest.raises(ValueError):
        token_service.validate_access_token(pair.access_token)


@pytest.mark.asyncio
async def test_validate_rejects_garbage_token(token_service: JwtTokenService):
    with pytest.raises(ValueError):
        token_service.validate_access_token("not-a-jwt")
