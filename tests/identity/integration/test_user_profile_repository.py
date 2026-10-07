import uuid

import pytest
from sqlalchemy.exc import IntegrityError

from src.identity.domain.entities.user_profile import UserProfile


@pytest.mark.asyncio
async def test_add_and_get_user_by_id(profile_repo):
    profile = UserProfile(id=uuid.uuid4(), account_id=uuid.uuid4(), name="Ivan", address="Moscow")

    await profile_repo.add_user(profile)

    fetched = await profile_repo.get_user_by_id(profile.id)

    assert fetched is not None
    assert fetched.id == profile.id
    assert fetched.account_id == profile.account_id
    assert fetched.name == "Ivan"
    assert fetched.address == "Moscow"


@pytest.mark.asyncio
async def test_get_user_by_account_id(profile_repo):
    account_id = uuid.uuid4()
    profile = UserProfile(id=uuid.uuid4(), account_id=account_id, name="Petr")

    await profile_repo.add_user(profile)

    fetched = await profile_repo.get_user_by_account_id(account_id)

    assert fetched is not None
    assert fetched.id == profile.id


@pytest.mark.asyncio
async def test_get_user_by_account_id_not_found(profile_repo):
    assert await profile_repo.get_user_by_account_id(uuid.uuid4()) is None


@pytest.mark.asyncio
async def test_update_user(profile_repo):
    profile = UserProfile(
        id=uuid.uuid4(), account_id=uuid.uuid4(), name="Old Name", address="Old Address"
    )
    await profile_repo.add_user(profile)

    profile.name = "New Name"
    profile.address = "New Address"
    await profile_repo.update_user(profile)

    fetched = await profile_repo.get_user_by_id(profile.id)
    assert fetched.name == "New Name"
    assert fetched.address == "New Address"


@pytest.mark.asyncio
async def test_delete_user(profile_repo):
    profile = UserProfile(id=uuid.uuid4(), account_id=uuid.uuid4(), name="Doomed")
    await profile_repo.add_user(profile)

    await profile_repo.delete_user(profile.id)

    assert await profile_repo.get_user_by_id(profile.id) is None


@pytest.mark.asyncio
async def test_duplicate_account_id_violates_unique_constraint(profile_repo):
    account_id = uuid.uuid4()
    await profile_repo.add_user(UserProfile(id=uuid.uuid4(), account_id=account_id))

    with pytest.raises(IntegrityError):
        await profile_repo.add_user(UserProfile(id=uuid.uuid4(), account_id=account_id))
