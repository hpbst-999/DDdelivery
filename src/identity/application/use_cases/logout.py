from src.identity.application.interfaces import IUnitOfWork

class LogoutUseCase:
    def __init__(self, uow: IUnitOfWork):
        self.uow = uow 

    async def execute(self, refresh_token: str) -> None:
        async with self.uow:
            await self.uow.refresh_tokens.revoke_token(refresh_token)