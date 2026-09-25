import uuid

from src.courier.application.interfaces import IUnitOfWork
from src.courier.domain.entities.courier_profile import CourierProfile


class CreateCourierUseCase:
    
    def __init__(self,  uow: IUnitOfWork):
        self.uow = uow

    async def execute(self, account_id: uuid.UUID) -> None:
        async with self.uow:
            courier_profile = await self.uow.courier_profiles.get_profile_by_account_id(account_id)
            if not courier_profile:
                courier_id = uuid.uuid4()

                courier_profile = CourierProfile(id=courier_id, account_id=account_id)
                await self.uow.courier_profiles.add_courier(courier_profile)

            await self.uow.commit()

            