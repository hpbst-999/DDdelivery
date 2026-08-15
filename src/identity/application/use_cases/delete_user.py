import uuid
from src.identity.application.interfaces import IUnitOfWork
from src.identity.domain.exceptions import DomainException,AccountNotFoundError
from src.identity.domain.value_objects.enums import AccountRole

class DeleteUserUseCase:
    
    def __init__(self, uow: IUnitOfWork):
        self.uow = uow

    def execute(self, account_id: uuid.UUID) -> None:
        with self.uow:
            account = self.uow.accounts.get_account_by_id(account_id)
            if not account:
                raise AccountNotFoundError("Account not found")
            if not account.has_role(AccountRole.USER):
                raise DomainException("The account does not have a user profile")
            
            self.uow.user_profiles.delete_user(account_id)
            account.remove_role(AccountRole.USER)

            if not account.roles:
                self.uow.accounts.delete_account(account_id)
            else:
                self.uow.accounts.update_account(account)