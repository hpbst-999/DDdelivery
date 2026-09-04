import uuid
from src.identity.application.interfaces import IUnitOfWork
from src.identity.domain.entities.user_profile import UserProfile
from src.identity.domain.exceptions import ProfileNotFoundError

class GetUserProfileUseCase:
    def __init__(self, uow: IUnitOfWork):
        self.uow = uow

    async def execute(self, profile_id: uuid.UUID) -> UserProfile:
        async with self.uow:
            profile = await self.uow.user_profiles.get_user_by_id(profile_id)
            if not profile:
                raise ProfileNotFoundError("User profile not found")
            return profile