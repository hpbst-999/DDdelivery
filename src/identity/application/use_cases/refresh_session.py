import uuid
from datetime import UTC, datetime, timedelta

from src.identity.application.interfaces import (
    ITokenGenerator,
    ITokenValidator,
    IUnitOfWork,
    ITokenData
)
from src.identity.domain.entities.refresh_token import RefreshToken
from src.identity.domain.exceptions import (
    InvalidTokenError,
    SessionNotFoundError,
    TokenExpiredError,
)


class RefreshSessionUseCase:
    def __init__(
        self, uow: IUnitOfWork, token_generator: ITokenGenerator, token_validator: ITokenValidator
    ):
        self.uow = uow
        self.token_generator = token_generator
        self.token_validator = token_validator

    async def execute(self, raw_refresh_token: str) -> ITokenData:
        try:
            self.token_validator.validate_refresh_token(raw_refresh_token)
        except ValueError:
            raise InvalidTokenError

        async with self.uow:
            token = await self.uow.refresh_tokens.get_refresh_token(raw_refresh_token)
            if not token:
                raise SessionNotFoundError("Session not found")

            if not token.is_valid:
                token.revoke()
                await self.uow.refresh_tokens.save_refresh_token(token)
                await self.uow.commit()
                raise TokenExpiredError("Refresh token has expired")

            token.revoke()
            await self.uow.refresh_tokens.save_refresh_token(token)

            token_pair = self.token_generator.generate_pair(account_id=token.account_id)
            now = datetime.now(UTC)
            new_token = RefreshToken(
                id=uuid.uuid4(),
                account_id=token.account_id,
                refresh_token=token_pair.refresh_token,
                expires_at=now + timedelta(days=30),
                created_at=now,
            )
            await self.uow.refresh_tokens.save_refresh_token(new_token)

            await self.uow.commit()
        return token_pair
