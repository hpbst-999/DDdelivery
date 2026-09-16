import uuid
from datetime import datetime, timedelta, timezone

from src.identity.application.dtos.oauth_user import OAuthUser
from src.identity.application.interfaces import IUnitOfWork, ITokenService, TokenPair
from src.identity.domain.entities.account import Account
from src.identity.domain.entities.courier_profile import CourierProfile
from src.identity.domain.value_objects.email import Email
from src.identity.domain.value_objects.enums import AccountRole


class LoginCourierWithOAuthUseCase:
    def __init__(self, uow: IUnitOfWork,token_service: ITokenService):
        self.uow = uow
        self.token_service = token_service

    async def execute(self, user_info: OAuthUser) -> TokenPair:
        email = Email(user_info.email)

        async with self.uow:
            account = await self.uow.accounts.get_account_by_email(email)
            if account:
                if not account.has_role(AccountRole.COURIER):
                    account.add_role(AccountRole.COURIER)
                    new_profile = CourierProfile(id=account.id)
                    await self.uow.courier_profiles.add_courier(new_profile)
                    await self.uow.accounts.update_account(account)
                account_id = str(account.id)
                
            else:
                new_account_id = uuid.uuid4()
                new_account = Account(
                    id=new_account_id,
                    roles=[AccountRole.COURIER],
                    email=email
                )
                new_profile = CourierProfile(id=new_account.id)
                await self.uow.accounts.add_account(new_account)
                await self.uow.courier_profiles.add_courier(new_profile)
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