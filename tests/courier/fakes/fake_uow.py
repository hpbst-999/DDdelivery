import uuid

from src.courier.application.interfaces import ICourierProfileRepository, IUnitOfWork
from src.courier.domain.entities.courier_profile import CourierProfile


class FakeCourierProfileRepository(ICourierProfileRepository):
    def __init__(self) -> None:
        self._data: dict[uuid.UUID, CourierProfile] = {}

    async def get_courier_by_id(self, profile_id: uuid.UUID) -> CourierProfile | None:
        return self._data.get(profile_id)

    async def get_courier_by_account_id(self, account_id: uuid.UUID) -> CourierProfile | None:
        for profile in self._data.values():
            if profile.account_id == account_id:
                return profile
        return None

    async def add_courier(self, profile: CourierProfile) -> None:
        self._data[profile.id] = profile

    async def update_courier(self, profile: CourierProfile) -> None:
        self._data[profile.id] = profile

    async def delete_courier(self, account_id: uuid.UUID) -> None:
        profile = await self.get_courier_by_account_id(account_id)
        if profile:
            del self._data[profile.id]


class FakeUnitOfWork(IUnitOfWork):
    courier_profiles: FakeCourierProfileRepository

    def __init__(self) -> None:
        self.courier_profiles = FakeCourierProfileRepository()
        self.committed: bool = False
        self.rolled_back: bool = False

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.rolled_back = True

    async def commit(self):
        self.committed = True
