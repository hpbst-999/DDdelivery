import uuid
import pytest
from datetime import datetime, timedelta, timezone
from unittest.mock import patch

from tests.identity.fakes.fake_uow import FakeUnitOfWork
from src.identity.application.use_cases.request_otp import RequestOTPUseCase
from src.identity.domain.entities.OTP import OTP
from src.identity.domain.value_objects.phone_number import PhoneNumber
from src.identity.domain.exceptions import OTPRateLimitError

@pytest.fixture
def uow():
    return FakeUnitOfWork()

@pytest.fixture
def use_case(uow):
    return RequestOTPUseCase(uow=uow)

@pytest.fixture
def target_phone():
    return "+79991234567"


@pytest.mark.asyncio
async def test_request_otp_first_time_success(use_case, uow, target_phone):
    session_id = await use_case.execute(raw_phone_number=target_phone)
    assert isinstance(session_id, uuid.UUID)
    
    saved_otp = await uow.otp.get_latest_otp_by_phone(PhoneNumber(target_phone))
    assert saved_otp is not None
    assert saved_otp.session_id == session_id
    
    assert len(uow.outbox.messages) == 1
    outbox_msg = uow.outbox.messages[0]
    assert outbox_msg.type == "identity.otp_created"
    assert outbox_msg.payload["code"] == saved_otp.code
    
    assert uow.committed is True


@pytest.mark.asyncio
@patch("src.identity.domain.entities.OTP.datetime") # Укажи точный путь до datetime в твоем файле OTP.py
async def test_request_otp_rate_limit_error(mock_datetime, use_case, uow, target_phone):
    now = datetime(2026, 1, 1, 12, 0, tzinfo=timezone.utc)
    mock_datetime.now.return_value = now
    first_otp = OTP.generate_otp(phone=PhoneNumber(target_phone))
    await uow.otp.save_otp(first_otp)
    with pytest.raises(OTPRateLimitError):
        await use_case.execute(raw_phone_number=target_phone)
    assert uow.committed is False
    assert len(uow.outbox.messages) == 0


@pytest.mark.asyncio
@patch("src.identity.domain.entities.OTP.datetime")
async def test_request_otp_after_cooldown_invalidates_old_otp(mock_datetime, use_case, uow, target_phone):
    past_time = datetime(2026, 1, 1, 12, 0, tzinfo=timezone.utc)
    mock_datetime.now.return_value = past_time
    old_otp = OTP.generate_otp(phone=PhoneNumber(target_phone))
    await uow.otp.save_otp(old_otp)
    assert old_otp.is_used is False  # Сначала он активен
    future_time = past_time + timedelta(minutes=2)
    mock_datetime.now.return_value = future_time
    new_session_id = await use_case.execute(raw_phone_number=target_phone)
    assert old_otp.is_used is True
    latest_otp = await uow.otp.get_latest_otp_by_phone(PhoneNumber(target_phone))
    assert latest_otp.session_id == new_session_id
    assert latest_otp.session_id != old_otp.session_id
    assert len(uow.outbox.messages) == 1
    assert uow.outbox.messages[0].payload["code"] == latest_otp.code
    assert uow.committed is True