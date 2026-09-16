import uuid

from src.identity.application.interfaces import IUnitOfWork, ICacheRepository
from src.identity.domain.entities.user_profile import UserProfile
from src.identity.domain.exceptions import ProfileNotFoundError


class GetUserProfileUseCase:
    def __init__(self, uow: IUnitOfWork, cache: ICacheRepository):
        self.uow = uow
        self.cache = cache

    async def execute(self, profile_id: uuid.UUID) -> UserProfile:
        cache_key = f"user_profile:{profile_id}"
        cached_data = await self.cache.get(cache_key)
        if cached_data:
            return UserProfile.from_dict(cached_data)

        async with self.uow:
            profile = await self.uow.user_profiles.get_user_by_id(profile_id)

        if not profile:
            raise ProfileNotFoundError("User profile not found")
        
        await self.cache.set(cache_key, profile.to_dict(), ttl_second=600)
        return profile
        