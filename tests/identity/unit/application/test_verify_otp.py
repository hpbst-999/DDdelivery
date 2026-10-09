import uuid
from datetime import UTC, datetime, timedelta

import pytest

from src.identity.application.use_cases.verify_otp import VerifyOTPUseCase
from src.identity.domain.entities.OTP import OTP
from src.identity.domain.exceptions import (
    InvalidOTPCodeError,
    OTPSessionNotFoundError,
)
from src.identity.domain.value_objects.phone_number import PhoneNumber
from tests.identity.fakes.fake_uow import FakeUnitOfWork


@pytest.fixture
def active_otp() -> OTP:
    now = datetime.now(UTC)
    return OTP(
        session_id=uuid.uuid4(),
        phone_number=PhoneNumber("+79991234567"),
        code="1234",
        created_at=now,
        expires_at=now + timedelta(minutes=10),
        attempts_count=0,
        max_attempts=3,
        is_used=False,
    )


@pytest.mark.asyncio
async def test_verify_otp_success(active_otp: OTP) -> None:
    uow = FakeUnitOfWork()
    await uow.otp.save_otp(active_otp)
    use_case = VerifyOTPUseCase(uow=uow)

    result = await use_case.execute(
        session_id=active_otp.session_id, 
        input_code="1234"
    )

    assert result == active_otp.phone_number
    
    updated_otp = await uow.otp.get_otp_by_session(active_otp.session_id)
    assert updated_otp.is_used is True


@pytest.mark.asyncio
async def test_verify_otp_session_not_found() -> None:
    uow = FakeUnitOfWork() 
    use_case = VerifyOTPUseCase(uow=uow)
    session_id = uuid.uuid4()

    with pytest.raises(OTPSessionNotFoundError, match="OTP session not found"):
        await use_case.execute(session_id=session_id, input_code="1234")

    assert uow.committed is False


@pytest.mark.asyncio
async def test_verify_otp_invalid_code_saves_attempt_and_commits(active_otp: OTP) -> None:
    uow = FakeUnitOfWork()
    await uow.otp.save_otp(active_otp)
    use_case = VerifyOTPUseCase(uow=uow)

    with pytest.raises(InvalidOTPCodeError):
        await use_case.execute(
            session_id=active_otp.session_id, 
            input_code="0000" 
        )

    updated_otp = await uow.otp.get_otp_by_session(active_otp.session_id)
    assert updated_otp.attempts_count == 1
    assert updated_otp.is_used is False
    
    assert uow.committed is True