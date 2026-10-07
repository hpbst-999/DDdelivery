import uuid

import pytest
from sqlalchemy import select

from src.identity.domain.entities.account import Account
from src.identity.domain.exceptions import DomainException
from src.identity.domain.value_objects.phone_number import PhoneNumber
from src.identity.infrastructure.models import AccountModel


@pytest.mark.asyncio
async def test_commit_persists_changes_visible_on_the_same_connection(uow, session):
    account = Account(id=uuid.uuid4(), phone_number=PhoneNumber("+79991110000"))

    async with uow:
        await uow.accounts.add_account(account)
        await uow.commit()

    result = await session.scalars(select(AccountModel).where(AccountModel.id == account.id))
    assert result.one_or_none() is not None


@pytest.mark.asyncio
async def test_exception_inside_context_rolls_back(uow, session):
    account = Account(id=uuid.uuid4(), phone_number=PhoneNumber("+79992220000"))

    with pytest.raises(DomainException):
        async with uow:
            await uow.accounts.add_account(account)
            raise DomainException("boom")

    result = await session.scalars(select(AccountModel).where(AccountModel.id == account.id))
    assert result.one_or_none() is None
