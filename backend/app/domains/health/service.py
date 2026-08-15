from app.domains.health.schemas import DbHealthData, HealthData
from app.domains.health.repository import HealthRepository


def check_service_health() -> HealthData:
    return HealthData(status="ok", service="backend")


def check_database_health(repository: HealthRepository) -> DbHealthData:
    result = repository.ping()
    return DbHealthData(status="ok", db="connected", result=int(result))
