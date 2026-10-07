import uuid

from src.identity.application.interfaces import IUnitOfWork
from src.identity.domain.exceptions import (
    InvalidOTPCodeError,
    OTPSessionNotFoundError,
)
from src.identity.domain.value_objects.phone_number import PhoneNumber


class VerifyOTPUseCase:
    def __init__(self, uow: IUnitOfWork):
        self.uow = uow

    async def execute(self, session_id: uuid.UUID, input_code: str) -> PhoneNumber:
        async with self.uow:
            otp = await self.uow.otp.get_otp_by_session(session_id)
            if not otp:
                raise OTPSessionNotFoundError("OTP session not found")

            try:
                otp.verify(input_code)
                await self.uow.otp.update_otp(otp)
            except InvalidOTPCodeError:
                await self.uow.otp.update_otp(otp)
                await self.uow.commit()
                raise

            return otp.phone_number
