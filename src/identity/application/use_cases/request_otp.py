from src.identity.domain.value_objects.phone_number import PhoneNumber
from src.identity.domain.entities.OTP import OTP
from src.identity.application.interfaces import IUnitOfWork
from src.identity.domain.exceptions import OTPRateLimitError
from src.outbox.domain.outbox_message import OutboxMessage
import uuid

class RequestOTPUseCase:
    def __init__(self, uow: IUnitOfWork):
        self.uow = uow

    async def execute(self, raw_phone_number: str) -> str:
        phone_number = PhoneNumber(raw_phone_number)

        async with self.uow:
            latest_otp = await self.uow.otp.get_latest_otp_by_phone(phone_number)

            if latest_otp:
                if not latest_otp.can_resend():
                    raise OTPRateLimitError("Too many OTP requests.")

                if not latest_otp.is_used:
                    latest_otp.is_used = True
                    await self.uow.otp.update_otp(latest_otp)

            new_otp = OTP.generate_otp(phone=phone_number)
            await self.uow.otp.save_otp(new_otp)

            outbox_event = OutboxMessage(
                id=uuid.uuid4(),
                type="identity.otp_created",
                payload={
                    "phone_number": new_otp.phone_number,
                    "code": new_otp.code,})
            
            await self.uow.outbox.add(outbox_event)
        
        return new_otp.session_id