import uuid
from src.courier.application.interfaces import IUnitOfWork
from src.courier.domain.value_objects.enums import CourierStatus

class ChangeCourierStatusUseCase:
    def __init__(self, uow: IUnitOfWork):
        self.uow = uow

    async def execute(self, account_id: uuid.UUID, target_status: CourierStatus) -> None:
        async with self.uow:
            profile = await self.uow.courier_profiles.get_profile_by_id(account_id)
            if not profile:
                raise ValueError("Coureir profile not found.")
            if profile.status == target_status:
                return 

            if profile.status == CourierStatus.BUSY and target_status == CourierStatus.OFFLINE:
                raise ValueError("You cannot complete the shift while you have an active order")
            if target_status == CourierStatus.BUSY:
                raise ValueError("The BUSY status is set by the system")

            profile.status = target_status
            
            await self.uow.courier_profiles.update_courier(profile)
            await self.uow.commit()