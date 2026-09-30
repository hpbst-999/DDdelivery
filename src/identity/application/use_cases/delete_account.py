import uuid

from src.identity.application.interfaces import IUnitOfWork
from src.identity.domain.exceptions import AccountNotFoundError


class DeleteAccountUseCase:

    def __init__(self, uow: IUnitOfWork):
        self.uow = uow

    async def execute(self, id: uuid.UUID) -> None:
        async with self.uow:
            account = await self.uow.accounts.get_account_by_id(id)
            if not account:
                raise AccountNotFoundError("Account not found")

            await self.uow.user_profiles.delete_user(id)
            await self.uow.accounts.delete_account(id)
            # как тут реализовать каскадное удаление профилей
            await self.uow.commit()
