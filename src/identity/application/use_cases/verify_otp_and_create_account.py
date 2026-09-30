import uuid
from datetime import UTC, datetime, timedelta

from src.identity.application.interfaces import ITokenService, IUnitOfWork, TokenPair
from src.identity.domain.entities.account import Account
from src.identity.domain.entities.user_profile import UserProfile
from src.identity.domain.exceptions import (
    InvalidOTPCodeError,
    OTPSessionNotFoundError,
)


class VerifyOTPAndCreateAccountUseCase:

    def __init__(self, uow: IUnitOfWork, token_service: ITokenService):
        self.uow = uow
        self.token_service = token_service

    async def execute(self, session_id: str, input_code: str) -> TokenPair:
        session_id = uuid.UUID(session_id)
        async with self.uow:
            otp = await self.uow.otp.get_otp_by_session(session_id)
            if not otp:
                raise OTPSessionNotFoundError("OTP session not found.")

            try:
                otp.verify(input_code)
                await self.uow.otp.update_otp(otp)
            except InvalidOTPCodeError as e:
                await self.uow.otp.update_otp(otp)
                await self.uow.commit()
                raise e

            phone_number = otp.phone_number

            account = await self.uow.accounts.get_account_by_phone(phone_number)
            if account:
                account_id = str(account.id)

            else:
                account_id = uuid.uuid4()
                account = Account(
                    id=account_id,
                    phone_number=phone_number
                )
                user_profile_id = uuid.uuid4()
                user_profile = UserProfile(id=user_profile_id, account_id=account.id)
                await self.uow.accounts.add_account(account)
                await self.uow.user_profiles.add_user(user_profile)
                account_id = str(account.id)

            tokens = self.token_service.generate_pair(account_id=account_id)
            new_id = uuid.uuid4()
            expires_at = datetime.now(UTC) + timedelta(days=30)

            await self.uow.refresh_tokens.save_refresh_token(
                    id=new_id,
                    account_id=account_id,
                    refresh_token=tokens["refresh_token"],
                    expires_at=expires_at,
                    created_at = datetime.now(UTC)
                )
            await self.uow.commit()

        return tokens
