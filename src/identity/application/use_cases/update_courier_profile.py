from src.identity.application.interfaces import IUnitOfWork
from src.identity.domain.exceptions import ProfileNotFoundError
from src.identity.domain.entities import CourierProfile

class UpdateCourierProfileUseCase:
    
    def __init__(self, pg_uow: IUnitOfWork):
        self.pg_uow = pg_uow

    def execute(self, account_id: str, name: str | None = None) -> CourierProfile:
        with self.pg_uow:
            profile = self.pg_uow.courier_profiles.get_courier_by_id(account_id)
            if not profile:
                raise ProfileNotFoundError("Courier profile not found")

            if name is not None:
                profile.name = name

            self.pg_uow.courier_profiles.update_courier(profile)
            self.pg_uow.commit()
            
        return profile