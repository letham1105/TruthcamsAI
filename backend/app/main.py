from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.db.base import Base
from backend.app.db.database import engine
from backend.app.models import User, VerificationSession
from backend.app.core.config import (
    API_V1_PREFIX,
    PROJECT_NAME,
    PROJECT_DESCRIPTION,
    PROJECT_VERSION,
    FRONTEND_ORIGIN,
)
from backend.app.api.v1.router import router as api_router


app = FastAPI(
    title=PROJECT_NAME,
    description=PROJECT_DESCRIPTION,
    version=PROJECT_VERSION,
)


@app.on_event("startup")
def create_database_tables():
    Base.metadata.create_all(bind=engine)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_ORIGIN],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(
    api_router,
    prefix=API_V1_PREFIX,
)


@app.get("/")
def root():
    return {
        "message": "Welcome to TruthCams AI",
        "status": "running",
    }