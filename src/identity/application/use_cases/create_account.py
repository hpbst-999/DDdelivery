import uuid
from datetime import UTC, datetime, timedelta

from src.core.config import settings
from src.identity.application.interfaces import ITokenGenerator, IUnitOfWork, TokenPair
from src.identity.domain.entities.account import Account
from src.identity.domain.entities.refresh_token import RefreshToken
from src.identity.domain.entities.user_profile import UserProfile
from src.identity.domain.exceptions import DomainException
from src.identity.domain.value_objects.email import Email
from src.identity.domain.value_objects.phone_number import PhoneNumber


class CreateAccountUseCase:
    def __init__(self, uow: IUnitOfWork, token_generator: ITokenGenerator):
        self.uow = uow
        self.token_generator = token_generator

    async def execute(
        self, phone_number: PhoneNumber | None = None, email: Email | None = None
    ) -> TokenPair:
        if (phone_number is None and email is None) or (
            phone_number is not None and email is not None
        ):
            raise DomainException

        async with self._uow:
            if phone_number is not None:
                account = await self.uow.accounts.get_account_by_phone(phone_number)
            else:
                account = await self.uow.accounts.get_account_by_email(email)

            if not account:
                account_id = uuid.uuid4()
                account = Account(id=account_id, phone_number=phone_number)
                user_profile_id = uuid.uuid4()
                user_profile = UserProfile(id=user_profile_id, account_id=account.id)
                await self.uow.accounts.add_account(account)
                await self.uow.user_profiles.add_user(user_profile)

            token_pair = self.token_generator.generate_pair(account_id=account.id)
            now = datetime.now(UTC)
            new_token = RefreshToken(
                id=uuid.uuid4(),
                account_id=account.id,
                refresh_token=token_pair.refresh_token,
                expires_at=now + timedelta(settings.REFRESH_TOKEN_EXPIRE_DAYS),
                created_at=now,
            )
            await self.uow.refresh_tokens.save_refresh_token(new_token)
            await self.uow.commit()

        return token_pair
