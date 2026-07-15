from src.identity.domain.value_objects import PhoneNumber
from src.identity.domain.entities import OTP
from src.identity.application.interfaces import IUnitOfWork,ISmsSender

class RequestOTPUseCase:
    def __init__(self, redis_uow: IUnitOfWork, sms_gateway: ISmsSender):
        self.redis_uow = redis_uow
        self.sms_gateway = sms_gateway

    def execute(self, raw_phone_number: str) -> str:
        phone_number = PhoneNumber(raw_phone_number)
        otp_entity = OTP.generate_otp(phone_number)

        with self.redis_uow:
            self.redis_uow.otp_repository.save_otp(otp_entity)
            self.redis_uow.commit()
        self.sms_gateway.send_sms(phone_number, f"your code: {otp_entity.code}")
        
        return otp_entity.session_id