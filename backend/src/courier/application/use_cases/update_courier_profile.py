import uuid

from src.courier.application.interfaces import IUnitOfWork
from src.courier.domain.exceptions import ProfileNotFoundError


class UpdateCourierProfileUseCase:
    def __init__(self, uow: IUnitOfWork):
        self.uow = uow

    async def execute(
        self, account_id: uuid.UUID, full_name: str | None = None, inn: str | None = None
    ) -> None:
        async with self.uow:
            profile = await self.uow.courier_profiles.get_courier_by_account_id(account_id)
            if not profile:
                raise ProfileNotFoundError("Courier profile not found")

            if full_name is not None:
                profile.full_name = full_name

            if inn is not None:
                profile.inn = inn

            await self.uow.courier_profiles.update_courier(profile)
            await self.uow.commit()
