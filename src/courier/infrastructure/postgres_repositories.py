import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.courier.domain.entities.courier_profile import CourierProfile
from src.courier.domain.value_objects.enums import CourierStatus
from src.courier.infrastructure.models import CourierProfileModel


class SQLAlchemyCourierProfileRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    def _to_entity(self, model: CourierProfileModel) -> CourierProfile:
        return CourierProfile(
            id=model.id,
            account_id=model.account_id,
            full_name=model.full_name,
            inn=model.inn,
            is_verified=model.is_verifed,
            verified_at=model.verified_at,
            status=CourierStatus(model.status)
        )

    async def get_courier_by_id(self, id: uuid.UUID) -> CourierProfile | None:
        stmt = select(CourierProfileModel).where(CourierProfileModel.id == id)
        result = await self.session.scalars(stmt)
        model = result.one_or_none()

        if not model:
            return None

        return self._to_entity(model=model)

    async def get_courier_by_account_id(self, account_id: uuid.UUID) -> CourierProfile | None:
            stmt = select(CourierProfileModel).where(CourierProfileModel.account_id == account_id)
            result = await self.session.scalars(stmt)
            model = result.one_or_none()

            if not model:
                return None

            return self._to_entity(model=model)

    async def add_courier(self, profile: CourierProfile) -> None:
        model = CourierProfileModel(
            id=profile.id,
            account_id = profile.account_id,
            full_name=profile.full_name,
            inn=profile.inn,
            is_verified=profile.is_verified,
            verified_at=profile.verified_at,
            status=profile.status
        )
        self.session.add(model)
        await self.session.flush()

    async def update_courier(self, profile: CourierProfile) -> None:
        stmt = select(CourierProfileModel).where(CourierProfileModel.id == profile.id)
        result = await self.session.scalars(stmt)
        model = result.one_or_none()

        if model:
            model.full_name = profile.full_name
            model.inn = profile.inn
            model.status = profile.status


    async def delete_courier(self,id: uuid.UUID) -> None:
        stmt = select(CourierProfileModel).where(CourierProfileModel.id == id)
        result = await self.session.scalars(stmt)
        model = result.one_or_none()
        if model:
            await self.session.delete(model)
            await self.session.flush()
