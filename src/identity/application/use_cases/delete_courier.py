from src.identity.application.interfaces import IUnitOfWork
from src.identity.domain.exceptions import AccountNotFoundError, DomainException
from src.identity.domain.entities import AccountRole

class DeleteCourierUseCase:
    
    def __init__(self, pg_uow: IUnitOfWork):
        self.pg_uow = pg_uow

    def execute(self, account_id: str) -> None:
        with self.pg_uow:
            account = self.pg_uow.accounts.get_account_by_id(account_id)
            if not account:
                raise AccountNotFoundError("Account not found")
            if not account.has_role(AccountRole.COURIER):
                raise DomainException("The account does not have a courier profile")
            
            self.pg_uow.courier_profiles.delete_courier(account_id)
            account.remove_role(AccountRole.COURIER)

            if not account.roles:
                self.pg_uow.accounts.delete_account(account_id)
            else:
                self.pg_uow.accounts.update_account(account)
            self.pg_uow.commit()