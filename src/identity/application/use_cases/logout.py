from src.identity.application.interfaces import IUnitOfWork


class LogoutUseCase:
    def __init__(self, uow: IUnitOfWork):
        self.uow = uow

    async def execute(self, refresh_token: str) -> None:
        async with self.uow:
            token = await self.uow.refresh_tokens.get_refresh_token(refresh_token=refresh_token)
            if token:
                token.revoke()
                await self.uow.refresh_tokens.save_refresh_token(token)

            await self.uow.commit()
