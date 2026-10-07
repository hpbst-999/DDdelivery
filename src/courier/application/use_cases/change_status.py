import uuid

from src.courier.application.interfaces import IUnitOfWork
from src.courier.domain.exceptions import ProfileNotFoundError
from src.courier.domain.value_objects.enums import CourierStatus


class ChangeCourierStatusUseCase:
    def __init__(self, uow: IUnitOfWork):
        self.uow = uow

    async def execute(self, account_id: uuid.UUID, target_status: CourierStatus) -> None:
        async with self.uow:
            profile = await self.uow.courier_profiles.get_courier_by_id(account_id)
            if not profile:
                raise ProfileNotFoundError("Coureir profile not found")

            profile.change_status(target_status)

            await self.uow.courier_profiles.update_courier(profile)
            await self.uow.commit()
