import uuid
import pytest
import pytest_asyncio

from tests.identity.fakes.fake_uow import FakeUnitOfWork, FakeCacheRepository
from src.identity.application.use_cases.update_user_profile import UpdateUserProfileUseCase
from src.identity.domain.entities.user_profile import UserProfile
from src.identity.domain.exceptions import ProfileNotFoundError


@pytest_asyncio.fixture
async def uow():
    return FakeUnitOfWork()

@pytest_asyncio.fixture
async def cache():
    return FakeCacheRepository()

@pytest.fixture
def use_case(uow, cache):
    return UpdateUserProfileUseCase(uow=uow, cache=cache)

@pytest.fixture
def existing_profile():
    return UserProfile(
        id=uuid.uuid4(),
        account_id=uuid.uuid4(),
        name="Old Name",
        address="Old Address"
    )


@pytest.mark.asyncio
async def test_update_profile_success_and_invalidates_cache(use_case, uow, cache, existing_profile):
    await uow.user_profiles.add_user(existing_profile)
    cache_key = f"user_profile:{existing_profile.id}"
    await cache.set(cache_key, existing_profile.to_dict())
    
    assert await cache.get(cache_key) is not None  

    updated_profile = await use_case.execute(
        id=existing_profile.id,
        name="New Name",
        address="New Address"
    )

    assert updated_profile.name == "New Name"
    assert updated_profile.address == "New Address"
    
    saved_profile = await uow.user_profiles.get_user_by_id(existing_profile.id)
    assert saved_profile.name == "New Name"
    
    assert uow.committed is True
    
    assert await cache.get(cache_key) is None


@pytest.mark.asyncio
async def test_update_profile_partial_update(use_case, uow, cache, existing_profile):
    await uow.user_profiles.add_user(existing_profile)

    updated_profile = await use_case.execute(
        id=existing_profile.id,
        name="Only Name Changed"
    )

    assert updated_profile.name == "Only Name Changed"
    assert updated_profile.address == "Old Address"
    assert uow.committed is True


@pytest.mark.asyncio
async def test_update_profile_not_found(use_case, uow):
    
    fake_id = uuid.uuid4()
    
    with pytest.raises(ProfileNotFoundError, match="User profile not found"):
        await use_case.execute(
            id=fake_id,
            name="Ghost",
            address="Nowhere"
        )
        
    assert uow.committed is False