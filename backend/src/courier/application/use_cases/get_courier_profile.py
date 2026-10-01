import uuid

from src.courier.application.interfaces import IUnitOfWork
from src.courier.domain.entities.courier_profile import CourierProfile
from src.courier.domain.exceptions import ProfileNotFoundError


class GetCourierProfileUseCase:
    def __init__(self, uow: IUnitOfWork):
        self.uow = uow

    async def execute(self, account_id: uuid.UUID) -> CourierProfile:
        async with self.uow:
            profile = await self.uow.courier_profiles.get_courier_by_account_id(account_id)
        if not profile:
            raise ProfileNotFoundError("Courier profile not found")

        return profile
