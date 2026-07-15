from src.identity.application.interfaces import IUnitOfWork
from src.identity.domain.exceptions import ProfileNotFoundError
from src.identity.domain.entities import UserProfile

class UpdateUserProfileUseCase:
    
    def __init__(self, pg_uow: IUnitOfWork):
        self.pg_uow = pg_uow

    def execute(self, account_id: str, name: str | None = None, address: str | None = None) -> UserProfile:
        with self.pg_uow:
            profile = self.pg_uow.user_profiles.get_user_by_id(account_id)
            if not profile:
                raise ProfileNotFoundError("User profile not found")

            if name is not None:
                profile.name = name
                
            if address is not None:
                profile.address = address

            self.pg_uow.user_profiles.update_user(profile)
            self.pg_uow.commit()

        return profile