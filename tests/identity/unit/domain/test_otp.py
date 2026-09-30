import uuid
from datetime import UTC, datetime, timedelta
from unittest.mock import patch

import pytest

from src.identity.domain.entities.OTP import OTP
from src.identity.domain.exceptions import (
    InvalidOTPCodeError,
    OTPExpiredError,
    OTPMaxAttemptsExceededError,
)
from src.identity.domain.services.otp_generator import OTPCodeGenerator
from src.identity.domain.value_objects.phone_number import PhoneNumber


@pytest.fixture
def phone():
    return PhoneNumber("+79991234567")

@pytest.fixture
def mock_now():
    return datetime(2026, 1, 1, 12, 0, 0, tzinfo=UTC)

@pytest.fixture
def valid_otp(phone, mock_now):
    return OTP(
        session_id=uuid.uuid4(),
        phone_number=phone,
        code="1234",
        created_at=mock_now,
        expires_at=mock_now + timedelta(minutes=10)
    )


def test_generate_otp_uses_injected_generator(phone):
    fake_generator = OTPCodeGenerator.generate_static

    otp = OTP.generate_otp(phone=phone, code_generator=fake_generator, ttl_min=15)

    assert otp.code == "9999"
    assert otp.max_attempts == 3
    assert otp.phone_number == phone
    assert otp.expires_at > otp.created_at


@patch("src.identity.domain.entities.OTP.datetime")
def test_can_resend_respects_cooldown(mock_datetime, valid_otp, mock_now):
    mock_datetime.now.return_value = mock_now
    assert valid_otp.can_resend(cooldown_seconds=60) is False

    mock_datetime.now.return_value = mock_now + timedelta(seconds=30)
    assert valid_otp.can_resend(cooldown_seconds=60) is False

    mock_datetime.now.return_value = mock_now + timedelta(seconds=65)
    assert valid_otp.can_resend(cooldown_seconds=60) is True

@patch("src.identity.domain.entities.OTP.datetime")
def test_is_expired(mock_datetime, valid_otp, mock_now):
    mock_datetime.now.return_value = mock_now + timedelta(minutes=5)
    assert valid_otp.is_expired() is False

    mock_datetime.now.return_value = mock_now + timedelta(minutes=11)
    assert valid_otp.is_expired() is True


@patch("src.identity.domain.entities.OTP.datetime")
def test_verify_success(mock_datetime, valid_otp, mock_now):
    mock_datetime.now.return_value = mock_now + timedelta(minutes=1)

    valid_otp.verify("1234")

    assert valid_otp.is_used is True
    assert valid_otp.attempts_count == 0

@patch("src.identity.domain.entities.OTP.datetime")
def test_verify_fails_with_invalid_code(mock_datetime, valid_otp, mock_now):
    mock_datetime.now.return_value = mock_now

    with pytest.raises(InvalidOTPCodeError) as exc_info:
        valid_otp.verify("0000")

    assert valid_otp.attempts_count == 1
    assert valid_otp.is_used is False
    assert "Attempts left" in str(exc_info.value)

@patch("src.identity.domain.entities.OTP.datetime")
def test_verify_fails_when_expired(mock_datetime, valid_otp, mock_now):
    mock_datetime.now.return_value = mock_now + timedelta(minutes=15)

    with pytest.raises(OTPExpiredError):
        valid_otp.verify("1234")

@patch("src.identity.domain.entities.OTP.datetime")
def test_verify_fails_when_max_attempts_exceeded(mock_datetime, valid_otp, mock_now):
    mock_datetime.now.return_value = mock_now
    valid_otp.attempts_count = 3

    with pytest.raises(OTPMaxAttemptsExceededError):
        valid_otp.verify("1234")

@patch("src.identity.domain.entities.OTP.datetime")
def test_verify_fails_if_already_used(mock_datetime, valid_otp, mock_now):
    mock_datetime.now.return_value = mock_now
    valid_otp.is_used = True

    with pytest.raises(InvalidOTPCodeError, match="has already been used"):
        valid_otp.verify("1234")
