from fastapi import APIRouter

from app.domains.debug.router import router as debug_router
from app.domains.health.router import router as health_router

router = APIRouter()
router.include_router(debug_router, prefix="/debug", tags=["debug"])
router.include_router(health_router, prefix="/health", tags=["health"])
