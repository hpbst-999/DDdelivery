import uuid
from src.identity.application.interfaces import IUnitOfWork
from src.identity.domain.entities import UserProfile
from src.identity.domain.exceptions import ProfileNotFoundError

class GetUserProfileUseCase:
    def __init__(self, pg_uow: IUnitOfWork):
        self.pg_uow = pg_uow

    def execute(self, profile_id: uuid.UUID) -> UserProfile:
        with self.pg_uow:
            profile = self.pg_uow.user_profiles.get_user_by_id(profile_id)
            if not profile:
                raise ProfileNotFoundError("User profile not found")
            return profile