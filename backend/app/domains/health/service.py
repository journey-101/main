from sqlalchemy import text
from sqlalchemy.orm import Session

from app.domains.health.schemas import DbHealthData, HealthData


def check_service_health() -> HealthData:
    return HealthData(status="ok", service="backend")


def check_database_health(session: Session) -> DbHealthData:
    result = session.execute(text("SELECT 1")).scalar_one()
    return DbHealthData(status="ok", db="connected", result=int(result))
