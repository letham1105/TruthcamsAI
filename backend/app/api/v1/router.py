from fastapi import APIRouter

from backend.app.api.v1.endpoints import health, verification, auth

router = APIRouter()

router.include_router(health.router)
router.include_router(verification.router)
router.include_router(auth.router)