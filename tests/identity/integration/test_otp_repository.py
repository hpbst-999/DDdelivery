import uuid
from datetime import UTC, datetime, timedelta

import pytest

from src.identity.domain.entities.OTP import OTP
from src.identity.domain.value_objects.phone_number import PhoneNumber


def make_otp(phone: str, **overrides) -> OTP:
    now = datetime.now(UTC)
    defaults = dict(
        session_id=uuid.uuid4(),
        phone_number=PhoneNumber(phone),
        code="1234",
        created_at=now,
        expires_at=now + timedelta(minutes=10),
    )
    defaults.update(overrides)
    return OTP(**defaults)


@pytest.mark.asyncio
async def test_save_and_get_otp_by_session(otp_repo):
    otp = make_otp("+79991234567")

    await otp_repo.save_otp(otp)

    fetched = await otp_repo.get_otp_by_session(otp.session_id)

    assert fetched is not None
    assert fetched.session_id == otp.session_id
    assert fetched.code == "1234"
    assert str(fetched.phone_number) == str(otp.phone_number)


@pytest.mark.asyncio
async def test_get_otp_by_session_not_found(otp_repo):
    assert await otp_repo.get_otp_by_session(uuid.uuid4()) is None


@pytest.mark.asyncio
async def test_get_latest_otp_by_phone_returns_most_recent(otp_repo):
    phone = "+79997654321"
    now = datetime.now(UTC)

    older = make_otp(phone, created_at=now - timedelta(minutes=5))
    newer = make_otp(phone, created_at=now)

    await otp_repo.save_otp(older)
    await otp_repo.save_otp(newer)

    latest = await otp_repo.get_latest_otp_by_phone(PhoneNumber(phone))

    assert latest is not None
    assert latest.session_id == newer.session_id


@pytest.mark.asyncio
async def test_get_latest_otp_by_phone_not_found(otp_repo):
    assert await otp_repo.get_latest_otp_by_phone(PhoneNumber("+79990000000")) is None


@pytest.mark.asyncio
async def test_update_otp_persists_attempts_and_usage(otp_repo, session):
    otp = make_otp("+79995556677")
    await otp_repo.save_otp(otp)

    otp.attempts_count = 2
    otp.is_used = True
    await otp_repo.update_otp(otp)
    await session.flush()
    session.expire_all()

    fetched = await otp_repo.get_otp_by_session(otp.session_id)
    assert fetched.attempts_count == 2
    assert fetched.is_used is True
