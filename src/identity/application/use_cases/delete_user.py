from src.identity.application.interfaces import IUnitOfWork
from src.identity.domain.exceptions import DomainException,AccountNotFoundError
from src.identity.domain.entities import AccountRole

class DeleteUserUseCase:
    
    def __init__(self, pg_uow: IUnitOfWork):
        self.pg_uow = pg_uow

    def execute(self, account_id: str) -> None:
        with self.pg_uow:
            account = self.pg_uow.accounts.get_account_by_id(account_id)
            if not account:
                raise AccountNotFoundError("Account not found")
            if not account.has_role(AccountRole.USER):
                raise DomainException("The account does not have a user profile")
            
            self.pg_uow.user_profiles.delete_user(account_id)
            account.remove_role(AccountRole.USER)

            if not account.roles:
                self.pg_uow.accounts.delete_account(account_id)
            else:
                self.pg_uow.accounts.update_account(account)
            self.pg_uow.commit()