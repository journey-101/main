from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.errors import DatabaseConnectionError
from app.db.session import get_db_session
from app.domains.health.schemas import DbHealthData, HealthData, SuccessResponse
from app.domains.health.service import check_database_health, check_service_health

router = APIRouter()


@router.get("", response_model=SuccessResponse[HealthData])
def get_health() -> SuccessResponse[HealthData]:
    return SuccessResponse(data=check_service_health())


@router.get("/db", response_model=SuccessResponse[DbHealthData])
def get_database_health(
    session: Session = Depends(get_db_session),
) -> SuccessResponse[DbHealthData]:
    try:
        return SuccessResponse(data=check_database_health(session))
    except Exception as exc:
        raise DatabaseConnectionError() from exc
