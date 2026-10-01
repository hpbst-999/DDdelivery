import uuid
from datetime import UTC, datetime, timedelta

import pytest
import pytest_asyncio

from src.identity.application.use_cases.verify_otp_and_create_account import (
    VerifyOTPAndCreateAccountUseCase,
)
from src.identity.domain.entities.account import Account
from src.identity.domain.entities.OTP import OTP
from src.identity.domain.exceptions import DomainException, InvalidOTPCodeError
from src.identity.domain.value_objects.phone_number import PhoneNumber
from tests.identity.fakes.fake_uow import FakeUnitOfWork


class FakeTokenService:
    def generate_pair(self, account_id: str) -> dict:
        return {
            "access_token": f"access_for_{account_id}",
            "refresh_token": f"refresh_for_{account_id}",
        }


@pytest.fixture
def uow():
    return FakeUnitOfWork()


@pytest.fixture
def token_service():
    return FakeTokenService()


@pytest.fixture
def use_case(uow, token_service):
    return VerifyOTPAndCreateAccountUseCase(uow=uow, token_service=token_service)


@pytest.fixture
def target_phone():
    return "+79991234567"


@pytest.fixture
def valid_session_id():
    return uuid.uuid4()


@pytest_asyncio.fixture
async def pre_saved_otp(uow, target_phone, valid_session_id):
    now = datetime.now(UTC)
    otp = OTP(
        session_id=valid_session_id,
        phone_number=PhoneNumber(target_phone),
        code="1234",
        created_at=now,
        expires_at=now + timedelta(minutes=10),
    )
    await uow.otp.save_otp(otp)
    return otp


@pytest.mark.asyncio
async def test_verify_success_new_user(use_case, uow, pre_saved_otp):

    session_str = str(pre_saved_otp.session_id)
    tokens = await use_case.execute(session_id=session_str, input_code="1234")
    assert "access_token" in tokens
    assert "refresh_token" in tokens
    assert len(uow.accounts.accounts) == 1
    assert len(uow.user_profiles.profiles) == 1
    saved_acc = list(uow.accounts.accounts.values())[0]
    assert str(saved_acc.phone_number) == str(pre_saved_otp.phone_number)
    assert len(uow.refresh_tokens.tokens) == 1
    assert pre_saved_otp.is_used is True
    assert uow.committed is True


@pytest.mark.asyncio
async def test_verify_success_existing_user(use_case, uow, pre_saved_otp):
    existing_acc = Account(id=uuid.uuid4(), phone_number=pre_saved_otp.phone_number)
    await uow.accounts.add_account(existing_acc)

    session_str = str(pre_saved_otp.session_id)

    await use_case.execute(session_id=session_str, input_code="1234")

    assert len(uow.accounts.accounts) == 1
    assert len(uow.user_profiles.profiles) == 0
    assert uow.committed is True


@pytest.mark.asyncio
async def test_verify_invalid_code_saves_attempts(use_case, uow, pre_saved_otp):

    session_str = str(pre_saved_otp.session_id)

    with pytest.raises(InvalidOTPCodeError):
        await use_case.execute(session_id=session_str, input_code="0000")

    assert uow.committed is True
    assert pre_saved_otp.attempts_count == 1

    assert len(uow.accounts.accounts) == 0


@pytest.mark.asyncio
async def test_verify_session_not_found(use_case, uow):

    fake_session = str(uuid.uuid4())

    with pytest.raises(DomainException, match="OTP session not found"):
        await use_case.execute(session_id=fake_session, input_code="1234")
