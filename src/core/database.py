from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from src.core.config import settings

engine = create_engine(
    url=settings.database_url, 
    echo=True,
    pool_pre_ping=True,
    pool_size=5,       
    max_overflow=10  
)

SessionFactory = sessionmaker(
    autocommit=False, 
    autoflush=False, 
    bind=engine
)

Base = declarative_base()


def init_db() -> None:

    from src.identity.infrastructure.models import (
        AccountModel, 
        UserProfileModel, 
        CourierProfileModel,
        OTPModel
    )
    
    Base.metadata.create_all(bind=engine)