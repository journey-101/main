from typing import Annotated

from fastapi import APIRouter, Depends

from app.core.errors import DatabaseConnectionError
from app.db.uow import UnitOfWork, get_uow
from app.domains.health.schemas import DbHealthData, HealthData, SuccessResponse
from app.domains.health.service import check_database_health, check_service_health

router = APIRouter()


@router.get("", response_model=SuccessResponse[HealthData])
def get_health() -> SuccessResponse[HealthData]:
    return SuccessResponse(data=check_service_health())


@router.get("/db", response_model=SuccessResponse[DbHealthData])
def get_database_health(
    uow: Annotated[UnitOfWork, Depends(get_uow)],
) -> SuccessResponse[DbHealthData]:
    try:
        return SuccessResponse(data=check_database_health(uow.health))
    except Exception as exc:
        raise DatabaseConnectionError() from exc
