import uuid
from src.identity.application.interfaces import IUnitOfWork
from src.identity.domain.entities import CourierProfile
from src.identity.domain.exceptions import ProfileNotFoundError

class GetCourierProfileUseCase:
    def __init__(self, pg_uow: IUnitOfWork):
        self.pg_uow = pg_uow

    def execute(self, account_id: uuid.UUID) -> CourierProfile:
        with self.pg_uow:
            profile = self.pg_uow.courier_profiles.get_courier_by_id(account_id)
            if not profile:
                raise ProfileNotFoundError("Courier profile not found")
            return profile