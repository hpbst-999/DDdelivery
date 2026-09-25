import uuid
from datetime import datetime, timedelta, timezone

from src.identity.application.dtos.oauth_user import OAuthUser
from src.identity.application.interfaces import IUnitOfWork, ITokenService, TokenPair
from src.identity.domain.entities.account import Account
from src.identity.domain.entities.user_profile import UserProfile
from src.identity.domain.value_objects.email import Email


class LoginWithOAuthUseCase:
    def __init__(self, uow: IUnitOfWork,token_service: ITokenService):
        self.uow = uow
        self.token_service = token_service

    async def execute(self, user_info: OAuthUser) -> TokenPair:
        email = Email(user_info.email)

        async with self.uow:
            account = await self.uow.accounts.get_account_by_email(email)
            if account:
                account_id = str(account.id)
                
            else:
                account_id = uuid.uuid4()
                account = Account(
                    id=account_id,
                    email=email
                )
                user_profile_id = uuid.uuid4()
                user_profile = UserProfile(id=user_profile_id, account_id=account.id,name=user_info.name)
                await self.uow.accounts.add_account(account)
                await self.uow.user_profiles.add_user(user_profile)
                account_id = str(account.id)

            tokens = self.token_service.generate_pair(account_id=account_id)
            token_id = uuid.uuid4()
            expires_at = datetime.now(timezone.utc) + timedelta(days=30)

            await self.uow.refresh_tokens.save_refresh_token(
                    id=token_id,
                    account_id=account_id,
                    refresh_token=tokens["refresh_token"],
                    expires_at=expires_at,
                    created_at = datetime.now(timezone.utc)
                )

        return tokens