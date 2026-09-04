from src.identity.application.interfaces import IUnitOfWork
from src.identity.domain.exceptions import ProfileNotFoundError
from src.identity.domain.entities.courier_profile import CourierProfile

class UpdateCourierProfileUseCase:
    
    def __init__(self, uow: IUnitOfWork):
        self.uow = uow

    async def execute(self, account_id: str, name: str | None = None) -> CourierProfile:
        async with self.uow:
            profile = await self.uow.courier_profiles.get_courier_by_id(account_id)
            if not profile:
                raise ProfileNotFoundError("Courier profile not found")

            if name is not None:
                profile.name = name

            await self.uow.courier_profiles.update_courier(profile)
            
        return profile