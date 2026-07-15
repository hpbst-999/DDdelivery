# main.py
from fastapi import FastAPI
from src.identity.presentation.api.routes import router as identity_router
from src.core.database import init_db
# init_db()
app = FastAPI()


app.include_router(identity_router, prefix="/api/v1/auth")