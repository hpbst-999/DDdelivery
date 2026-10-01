import uuid

from src.identity.application.interfaces import ICacheRepository, IUnitOfWork
from src.identity.domain.entities.user_profile import UserProfile
from src.identity.domain.exceptions import ProfileNotFoundError


class UpdateUserProfileUseCase:
    def __init__(self, uow: IUnitOfWork, cache: ICacheRepository):
        self.uow = uow
        self.cache = cache

    async def execute(
        self, account_id: uuid.UUID, name: str | None = None, address: str | None = None
    ) -> UserProfile:
        async with self.uow:
            profile = await self.uow.user_profiles.get_user_by_account_id(account_id)
            if not profile:
                raise ProfileNotFoundError("User profile not found")

            if name is not None:
                profile.name = name

            if address is not None:
                profile.address = address

            await self.uow.user_profiles.update_user(profile)

            await self.uow.commit()

        cache_key = f"user_profile:{profile.account_id}"
        await self.cache.delete(cache_key)

        return profile
