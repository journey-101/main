from fastapi import APIRouter

from app.domains.auth.router import router as auth_router
from app.domains.directions.router import router as directions_router
from app.domains.health.router import router as health_router
from app.domains.places.router import router as places_router
from app.domains.recommendations.router import router as recommendations_router
from app.domains.trips.router import router as trips_router

router = APIRouter()
router.include_router(auth_router, prefix="/auth", tags=["auth"])
router.include_router(
    directions_router,
    prefix="/directions",
    tags=["directions"],
)
router.include_router(health_router, prefix="/health", tags=["health"])
router.include_router(places_router, prefix="/places", tags=["places"])
router.include_router(recommendations_router, tags=["recommendations"])
router.include_router(trips_router, prefix="/trips", tags=["trips"])
