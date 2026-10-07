import uuid

import pytest
from sqlalchemy.exc import IntegrityError

from src.identity.domain.entities.account import Account
from src.identity.domain.value_objects.email import Email
from src.identity.domain.value_objects.phone_number import PhoneNumber


@pytest.mark.asyncio
async def test_add_and_get_account_by_id(account_repo, session):
    account = Account(id=uuid.uuid4(), phone_number=PhoneNumber("+79991234567"))

    await account_repo.add_account(account)

    fetched = await account_repo.get_account_by_id(account.id)

    assert fetched is not None
    assert fetched.id == account.id
    assert str(fetched.phone_number) == str(account.phone_number)


@pytest.mark.asyncio
async def test_get_account_by_id_not_found(account_repo):
    fetched = await account_repo.get_account_by_id(uuid.uuid4())
    assert fetched is None


@pytest.mark.asyncio
async def test_get_account_by_phone(account_repo):
    phone = PhoneNumber("+79997654321")
    account = Account(id=uuid.uuid4(), phone_number=phone)
    await account_repo.add_account(account)

    fetched = await account_repo.get_account_by_phone(phone)

    assert fetched is not None
    assert fetched.id == account.id


@pytest.mark.asyncio
async def test_get_account_by_email(account_repo):
    email = Email("integration_test_user@example.com")
    account = Account(id=uuid.uuid4(), email=email)
    await account_repo.add_account(account)

    fetched = await account_repo.get_account_by_email(email)

    assert fetched is not None
    assert fetched.id == account.id


@pytest.mark.asyncio
async def test_update_account(account_repo, session):
    account = Account(id=uuid.uuid4(), phone_number=PhoneNumber("+79990001122"))
    await account_repo.add_account(account)

    account.email = Email("updated_user@example.com")
    await account_repo.update_account(account)
    await session.flush()

    fetched = await account_repo.get_account_by_id(account.id)
    assert fetched.email is not None
    assert str(fetched.email) == "updated_user@example.com"


@pytest.mark.asyncio
async def test_delete_account(account_repo):
    account = Account(id=uuid.uuid4(), phone_number=PhoneNumber("+79995554433"))
    await account_repo.add_account(account)

    await account_repo.delete_account(account.id)

    assert await account_repo.get_account_by_id(account.id) is None


@pytest.mark.asyncio
async def test_duplicate_phone_number_violates_unique_constraint(account_repo):
    phone = PhoneNumber("+79991112233")
    await account_repo.add_account(Account(id=uuid.uuid4(), phone_number=phone))

    with pytest.raises(IntegrityError):
        await account_repo.add_account(Account(id=uuid.uuid4(), phone_number=phone))
