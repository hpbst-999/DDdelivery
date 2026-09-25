from fastapi import FastAPI
from src.identity.presentation.api.routes import router as identity_router
from src.courier.presentation.api.routes import router as courier_router

app = FastAPI()


app.include_router(identity_router, prefix="/api/v1/auth")
app.include_router(courier_router, prefix="/api/v1/courier")