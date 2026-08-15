import uuid
from src.identity.application.interfaces import IUnitOfWork
from src.identity.domain.entities.user_profile import UserProfile
from src.identity.domain.exceptions import ProfileNotFoundError

class GetUserProfileUseCase:
    def __init__(self, uow: IUnitOfWork):
        self.uow = uow

    def execute(self, profile_id: uuid.UUID) -> UserProfile:
        with self.uow:
            profile = self.uow.user_profiles.get_user_by_id(profile_id)
            if not profile:
                raise ProfileNotFoundError("User profile not found")
            return profile