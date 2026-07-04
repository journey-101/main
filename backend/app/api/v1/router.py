from fastapi import APIRouter

from app.domains.debug.router import router as debug_router
from app.domains.health.router import router as health_router
from app.domains.places.router import router as places_router
from app.domains.trips.router import router as trips_router

router = APIRouter()
router.include_router(debug_router, prefix="/debug", tags=["debug"])
router.include_router(health_router, prefix="/health", tags=["health"])
router.include_router(places_router, prefix="/places", tags=["places"])
router.include_router(trips_router, prefix="/trips", tags=["trips"])
