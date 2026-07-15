from src.identity.application.interfaces import IUnitOfWork,ITokenService, TokenPair
from src.identity.domain.exceptions import DomainException,OTPVerificationFailedError
from src.identity.domain.entities import AccountRole, Account,UserProfile
import uuid

class VerifyOTPUAndCreateUserUseCase:
    
    def __init__(self, redis_uow: IUnitOfWork, pg_uow: IUnitOfWork, token_service: ITokenService):
        self.redis_uow = redis_uow
        self.pg_uow = pg_uow
        self.token_service = token_service

    def execute(self, session_id: str, input_code: str) -> TokenPair:
        with self.redis_uow:
            otp_entity = self.redis_uow.otp_repository.get_otp_by_session(session_id)
            if not otp_entity:
                raise DomainException("Session not found.")

            if otp_entity.is_expired():
                self.redis_uow.otp_repository.delete_otp_by_session(session_id)
                self.redis_uow.commit()
                raise DomainException("The code expired.")

            if otp_entity.code != input_code:
                raise OTPVerificationFailedError("Invalid code")

            phone_number = otp_entity.phone_number

        with self.pg_uow:
            account = self.pg_uow.accounts.get_account_by_phone(phone_number)
            if account:
                if not account.has_role(AccountRole.USER):
                    account.add_role(AccountRole.USER)
                    new_profile = UserProfile(id=account.id)
                    self.pg_uow.user_profiles.add_user(new_profile)
                    self.pg_uow.accounts.update_account(account)
                account_id = str(account.id)
                
            else:
                new_account_id = uuid.uuid4()
                new_account = Account(
                    id=new_account_id,
                    roles=[AccountRole.USER],
                    phone_number=phone_number
                )
                new_profile = UserProfile(id=new_account.id)
                self.pg_uow.accounts.add_account(new_account)
                self.pg_uow.user_profiles.add_user(new_profile)
                account_id = str(new_account.id)
            
            self.pg_uow.commit()

        tokens = self.token_service.generate_pair(account_id=account_id)
        new_session_id = str(uuid.uuid4())
        with self.redis_uow:
            self.redis_uow.otp_repository.delete_otp_by_session(session_id)
            self.redis_uow.session_repository.save_refresh_token(
                session_id=new_session_id,
                account_id=account_id,
                refresh_token=tokens["refresh_token"],
                expires_days=30
            )
            self.redis_uow.commit()

        return tokens