from src.identity.domain.value_objects.phone_number import PhoneNumber
from src.identity.domain.entities.OTP import OTP
from src.identity.application.interfaces import IUnitOfWork,ISmsSender
from src.identity.domain.exceptions import OTPRateLimitError
from src.outbox.domain.outbox_message import OutboxMessage
import uuid

class RequestOTPUseCase:
    def __init__(self, uow: IUnitOfWork, sms_gateway: ISmsSender):
        self.uow = uow
        self.sms_gateway = sms_gateway

    def execute(self, raw_phone_number: str) -> str:
        phone_number = PhoneNumber(raw_phone_number)

        with self.uow:
            latest_otp = self.uow.otp_repository.get_latest_otp_by_phone(phone_number)

            if latest_otp:
                if not latest_otp.can_resend():
                    raise OTPRateLimitError("Too many OTP requests.")

                if not latest_otp.is_used:
                    latest_otp.is_used = True
                    self.uow.otp_repository.update_otp(latest_otp)

            new_otp = OTP.generate_otp(phone=phone_number)
            self.uow.otp_repository.save_otp(new_otp)

            outbox_event = OutboxMessage(
                id=uuid.uuid4(),
                type="identity.otp_created",
                payload={
                    "phone_number": new_otp.phone_number.value,
                    "code": new_otp.code,})
            
            self.uow.outbox.add(outbox_event)
        
        self.sms_gateway.send_sms(phone_number, f"your code: {new_otp.code}")
        
        return new_otp.session_id