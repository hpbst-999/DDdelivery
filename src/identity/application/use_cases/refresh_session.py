import uuid
from src.identity.domain.exceptions import DomainException, SessionNotFoundError
from src.identity.application.interfaces import IUnitOfWork, ITokenService, TokenPair
from datetime import datetime, timedelta, timezone
class RefreshSessionUseCase:
    def __init__(self, uow: IUnitOfWork, token_service: ITokenService):
        self.uow = uow
        self.token_service = token_service

    async def execute(self, raw_refresh_token: str) -> TokenPair:
        try:
            self.token_service.validate_refresh_token(raw_refresh_token)
        except ValueError as e:
            raise DomainException(str(e))
        
        async with self.uow:
            session_data = await self.uow.refresh_tokens.get_data_by_token(raw_refresh_token)
            if not session_data:
                raise SessionNotFoundError("Session not found.")

            now = datetime.now(timezone.utc)
            if session_data.expires_at <= now:
                await self.uow.refresh_tokens.revoke_token(raw_refresh_token)
                raise DomainException("Refresh token has expired.")

            await self.uow.refresh_tokens.revoke_token(raw_refresh_token)

            account_id = session_data.account_id
            new_tokens = self.token_service.generate_pair(account_id=account_id)
            new_id = uuid.uuid4()
            expires_at = datetime.now(timezone.utc) + timedelta(days=30)

            await self.uow.refresh_tokens.save_refresh_token(
                id=new_id,
                account_id=account_id,
                refresh_token=new_tokens["refresh_token"],
                expires_at=expires_at,
                created_at = now
            )

        return new_tokens