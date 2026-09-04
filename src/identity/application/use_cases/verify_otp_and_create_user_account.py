from src.identity.application.interfaces import IUnitOfWork,ITokenService, TokenPair
from src.identity.domain.exceptions import InvalidOTPCodeError, DomainException
from src.identity.domain.value_objects.enums import AccountRole
from src.identity.domain.entities.account import Account
from src.identity.domain.entities.user_profile import UserProfile
import uuid
from datetime import datetime, timedelta, timezone

class VerifyOTPAndCreateUserUseCase:
    
    def __init__(self, uow: IUnitOfWork, token_service: ITokenService):
        self.uow = uow
        self.token_service = token_service

    async def execute(self, session_id: str, input_code: str) -> TokenPair:
        session_id = uuid.UUID(session_id)
        async with self.uow:
            otp = await self.uow.otp.get_otp_by_session(session_id)
            if not otp:
                raise DomainException("OTP session not found.") #поправить ошибку

            try:
                otp.verify(input_code)
            finally:
                await self.uow.otp.update_otp(otp)
                # self.uow.commit()         

            phone_number = otp.phone_number
        
            account = await self.uow.accounts.get_account_by_phone(phone_number)
            if account:
                if not account.has_role(AccountRole.USER):
                    account.add_role(AccountRole.USER)
                    new_profile = UserProfile(id=account.id)
                    await self.uow.user_profiles.add_user(new_profile)
                    await self.uow.accounts.update_account(account)
                account_id = str(account.id)
                
            else:
                new_account_id = uuid.uuid4()
                new_account = Account(
                    id=new_account_id,
                    roles=[AccountRole.USER],
                    phone_number=phone_number
                )
                new_profile = UserProfile(id=new_account.id)
                await self.uow.accounts.add_account(new_account)
                await self.uow.user_profiles.add_user(new_profile)
                account_id = str(new_account.id)

            tokens = self.token_service.generate_pair(account_id=account_id)
            new_id = uuid.uuid4()
            expires_at = datetime.now(timezone.utc) + timedelta(days=30)

            await self.uow.refresh_tokens.save_refresh_token(
                    id=new_id,
                    account_id=account_id,
                    refresh_token=tokens["refresh_token"],
                    expires_at=expires_at,
                    created_at = datetime.now(timezone.utc)
                )

        return tokens