import uuid
from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy.exc import IntegrityError

from src.identity.domain.entities.refresh_token import RefreshToken


def make_token(**overrides) -> RefreshToken:
    now = datetime.now(UTC)
    defaults = dict(
        id=uuid.uuid4(),
        account_id=uuid.uuid4(),
        refresh_token=f"token-{uuid.uuid4()}",
        expires_at=now + timedelta(days=30),
        created_at=now,
    )
    defaults.update(overrides)
    return RefreshToken(**defaults)


@pytest.mark.asyncio
async def test_save_and_get_refresh_token(refresh_token_repo):
    token = make_token()

    await refresh_token_repo.save_refresh_token(token)

    fetched = await refresh_token_repo.get_refresh_token(token.refresh_token)

    assert fetched is not None
    assert isinstance(fetched, RefreshToken)
    assert fetched.id == token.id
    assert fetched.account_id == token.account_id
    assert fetched.is_valid is True


@pytest.mark.asyncio
async def test_get_refresh_token_not_found(refresh_token_repo):
    assert await refresh_token_repo.get_refresh_token("does-not-exist") is None


@pytest.mark.asyncio
async def test_revoked_token_is_not_returned(refresh_token_repo):
    token = make_token()
    await refresh_token_repo.save_refresh_token(token)

    fetched = await refresh_token_repo.get_refresh_token(token.refresh_token)
    fetched.revoke()
    await refresh_token_repo.save_refresh_token(fetched)

    assert await refresh_token_repo.get_refresh_token(token.refresh_token) is None


@pytest.mark.asyncio
async def test_saving_an_already_persisted_token_again_updates_it_in_place(refresh_token_repo):
    token = make_token()
    await refresh_token_repo.save_refresh_token(token)

    token.revoke()
    await refresh_token_repo.save_refresh_token(token)


@pytest.mark.asyncio
async def test_duplicate_refresh_token_string_violates_unique_constraint(refresh_token_repo):
    shared_value = f"dup-{uuid.uuid4()}"
    await refresh_token_repo.save_refresh_token(make_token(refresh_token=shared_value))

    with pytest.raises(IntegrityError):
        await refresh_token_repo.save_refresh_token(make_token(refresh_token=shared_value))
