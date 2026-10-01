import uuid

from src.courier.application.interfaces import IUnitOfWork
from src.courier.domain.exceptions import ProfileNotFoundError


class DeleteCourierUseCase:
    def __init__(self, uow: IUnitOfWork):
        self.uow = uow

    async def execute(self, account_id: uuid.UUID) -> None:
        async with self.uow:
            courier_profile = await self.uow.courier_profiles.get_courier_by_account_id(account_id)

            if not courier_profile:
                raise ProfileNotFoundError("Courier profile not found")

            await self.uow.courier_profiles.delete_courier(account_id)
            await self.uow.commit()
