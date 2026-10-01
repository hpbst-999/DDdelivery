from uuid import UUID

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from src.identity.application.interfaces import (
    ICacheRepository,
    IUnitOfWork,
)
from src.identity.domain.entities.account import Account
from src.identity.infrastructure.security_jwt import JwtTokenService
from src.identity.presentation.dependencies import get_cache_repository, get_token_service, get_uow

security = HTTPBearer()


async def get_current_account(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    token_service: JwtTokenService = Depends(get_token_service),
    uow: IUnitOfWork = Depends(get_uow),
    cache: ICacheRepository = Depends(get_cache_repository),
) -> Account:
    token = credentials.credentials
    try:
        payload = token_service.validate_access_token(token)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    account_id = UUID(payload.get("sub"))
    if not account_id:
        raise HTTPException(status_code=401, detail="No ID found in token")

    cache_key = f"account:{account_id}"
    cache_account = await cache.get(key=cache_key)
    if cache_account:
        return Account.from_dict(cache_account)

    async with uow:
        account = await uow.accounts.get_account_by_id(account_id)
        if not account:
            raise HTTPException(status_code=401, detail="Account not found")
        await cache.set(cache_key, account.to_dict(), ttl_second=600)

        return account
