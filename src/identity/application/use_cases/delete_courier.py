import uuid
from src.identity.application.interfaces import IUnitOfWork
from src.identity.domain.exceptions import AccountNotFoundError, DomainException
from src.identity.domain.value_objects.enums import AccountRole

class DeleteCourierUseCase:
    
    def __init__(self, uow: IUnitOfWork):
        self.uow = uow

    async def execute(self, account_id: uuid.UUID) -> None:
        async with self.uow:
            account = await self.uow.accounts.get_account_by_id(account_id)
            if not account:
                raise AccountNotFoundError("Account not found")
            if not account.has_role(AccountRole.COURIER):
                raise DomainException("The account does not have a courier profile")
            
            await self.uow.courier_profiles.delete_courier(account_id)
            account.remove_role(AccountRole.COURIER)

            if not account.roles:
                await self.uow.accounts.delete_account(account_id)
            else:
                await self.uow.accounts.update_account(account)