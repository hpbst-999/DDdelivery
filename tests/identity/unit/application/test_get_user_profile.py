import uuid
import pytest
import pytest_asyncio

from tests.identity.fakes.fake_uow import FakeUnitOfWork, FakeCacheRepository
from src.identity.application.use_cases.get_user_profile import GetUserProfileUseCase
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
    return GetUserProfileUseCase(uow=uow, cache=cache)

@pytest.fixture
def existing_profile():
    return UserProfile(
        id=uuid.uuid4(),
        account_id=uuid.uuid4(),
        name="Ivan",
        address="Moscow"
    )

@pytest.mark.asyncio
async def test_get_profile_cache_miss_fetches_from_db_and_caches(use_case, uow, cache, existing_profile):
    
    await uow.user_profiles.add_user(existing_profile)
    cache_key = f"user_profile:{existing_profile.id}"
    
    assert await cache.get(cache_key) is None

    result = await use_case.execute(profile_id=existing_profile.id)

    assert result.id == existing_profile.id
    assert result.name == "Ivan"
    
    cached_data = await cache.get(cache_key)
    assert cached_data is not None
    assert cached_data["id"] == str(existing_profile.id)
    assert cached_data["name"] == "Ivan"


@pytest.mark.asyncio
async def test_get_profile_cache_hit_returns_fast(use_case, uow, cache, existing_profile):
    
    cache_key = f"user_profile:{existing_profile.id}"
    await cache.set(cache_key, existing_profile.to_dict())
    
    assert len(uow.user_profiles.profiles) == 0  

    result = await use_case.execute(profile_id=existing_profile.id)

    assert result.id == existing_profile.id
    assert result.name == "Ivan"


@pytest.mark.asyncio
async def test_get_profile_not_found_raises_error(use_case):
    
    random_id = uuid.uuid4()
    
    with pytest.raises(ProfileNotFoundError, match="User profile not found"):
        await use_case.execute(profile_id=random_id)