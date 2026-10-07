from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from src.identity.application.interfaces import ICacheRepository, ITokenValidator, IUnitOfWork
from src.identity.domain.entities.account import Account
from src.identity.presentation.dependencies import (
    get_cache_repository,
    get_token_validator,
    get_uow,
)

security = HTTPBearer(auto_error=True)


async def get_current_account_id(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    token_validator: ITokenValidator = Depends(get_token_validator),
) -> UUID:

    token = credentials.credentials
    try:
        payload = token_validator.validate_access_token(token)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )
    return payload["account_id"]


async def get_current_account(
    account_id: UUID = Depends(get_current_account_id),
    uow: IUnitOfWork = Depends(get_uow),
    cache: ICacheRepository = Depends(get_cache_repository),
) -> Account:
    cache_key = f"account:{account_id}"
    cache_account = await cache.get(key=cache_key)
    if cache_account:
        return Account.from_dict(cache_account)

    async with uow:
        account = await uow.accounts.get_account_by_id(account_id)
        if not account:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Account not found",
            )

        await cache.set(cache_key, account.to_dict(), ttl_second=600)
        return account
