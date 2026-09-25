from collections.abc import AsyncGenerator
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.database import SessionFactory

from src.courier.application.use_cases.delete_courier import DeleteCourierUseCase
from src.courier.application.use_cases.get_courier_profile import GetCourierProfileUseCase
from src.courier.application.use_cases.update_courier_profile import UpdateCourierProfileUseCase
from src.courier.application.use_cases.create_courier import CreateCourierUseCase
from src.courier.application.use_cases.change_status import ChangeCourierStatusUseCase
from src.courier.application.interfaces import IUnitOfWork
from src.courier.infrastructure.uow import SQLAlchemyUnitOfWork

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with SessionFactory() as session:
        yield session


def get_uow(session: AsyncSession = Depends(get_db)) -> IUnitOfWork:
    return SQLAlchemyUnitOfWork(session=session)

def get_update_courier_profile_use_case(
    uow: IUnitOfWork = Depends(get_uow)
) -> UpdateCourierProfileUseCase:
    return UpdateCourierProfileUseCase(uow=uow)

def get_delete_courier_use_case(
    uow: IUnitOfWork = Depends(get_uow)
) -> DeleteCourierUseCase:
    return DeleteCourierUseCase(uow=uow)

def get_courier_profile_use_case(
    uow: IUnitOfWork = Depends(get_uow)
) -> GetCourierProfileUseCase:
    return GetCourierProfileUseCase(uow=uow)

def get_create_courier_use_case(
    uow: IUnitOfWork = Depends(get_uow)
)-> CreateCourierUseCase:
    return CreateCourierUseCase(uow=uow)

async def get_change_courier_status_use_case(
    uow = Depends(get_uow)
) -> ChangeCourierStatusUseCase:
    return ChangeCourierStatusUseCase(uow=uow)
