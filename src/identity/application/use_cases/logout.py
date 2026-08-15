from src.identity.application.interfaces import IUnitOfWork

class LogoutUseCase:
    def __init__(self, uow: IUnitOfWork):
        self.uow = uow 

    def execute(self, raw_refresh_token: str) -> None:
        with self.uow:
            self.uow.refresh_tokens.revoke_token(raw_refresh_token)