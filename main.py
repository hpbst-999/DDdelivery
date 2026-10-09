from fastapi import FastAPI

from src.courier.presentation.api.routes import router as courier_router
from src.identity.presentation.api.routes import router as identity_router
from src.identity.presentation.security import get_current_account_id
from src.courier.presentation.dependencies import get_courier_account_id

app = FastAPI()

app.dependency_overrides[get_courier_account_id] = get_current_account_id

app.include_router(identity_router, prefix="/api/v1/auth")
app.include_router(courier_router, prefix="/api/v1/courier")
