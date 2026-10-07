import uuid

from src.identity.application.interfaces import IUnitOfWork
from src.identity.domain.exceptions import AccountNotFoundError


class DeleteAccountUseCase:
    def __init__(self, uow: IUnitOfWork):
        self.uow = uow

    async def execute(self, account_id: uuid.UUID) -> None:
        async with self.uow:
            account = await self.uow.accounts.get_account_by_id(account_id)
            if not account:
                raise AccountNotFoundError("Account not found")
            profile = await self.uow.user_profiles.get_user_by_account_id(account_id)
            if profile:
                await self.uow.user_profiles.delete_user(profile.id)
            await self.uow.accounts.delete_account(account_id)
            # как тут реализовать каскадное удаление профилей
            await self.uow.commit()
