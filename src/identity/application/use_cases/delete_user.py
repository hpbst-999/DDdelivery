import uuid
from src.identity.application.interfaces import IUnitOfWork
from src.identity.domain.exceptions import DomainException,AccountNotFoundError
from src.identity.domain.value_objects.enums import AccountRole

class DeleteUserUseCase:
    
    def __init__(self, uow: IUnitOfWork):
        self.uow = uow

    async def execute(self, account_id: uuid.UUID) -> None:
        async with self.uow:
            account = await self.uow.accounts.get_account_by_id(account_id)
            if not account:
                raise AccountNotFoundError("Account not found")
            if not account.has_role(AccountRole.USER):
                raise DomainException("The account does not have a user profile")
            
            await self.uow.user_profiles.delete_user(account_id)
            account.remove_role(AccountRole.USER)

            if not account.roles:
                await self.uow.accounts.delete_account(account_id)
            else:
                await self.uow.accounts.update_account(account)