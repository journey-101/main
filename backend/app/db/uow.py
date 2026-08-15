from collections.abc import Generator
from typing import Protocol

from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.domains.places.postgresql import PostgreSQLPlaceRepository
from app.domains.places.repository import PlaceRepository
from app.domains.recommendations.postgresql import PostgreSQLPreferenceRepository
from app.domains.recommendations.repository import PreferenceRepository
from app.domains.regions.postgresql import PostgreSQLInterestRegionRepository
from app.domains.regions.repository import InterestRegionRepository
from app.domains.trips.postgresql import PostgreSQLTripRepository
from app.domains.trips.repository import TripRepository
from app.domains.health.postgresql import PostgreSQLHealthRepository
from app.domains.health.repository import HealthRepository
from app.domains.users.postgresql import PostgreSQLUserRepository
from app.domains.users.repository import UserRepository


class UnitOfWork(Protocol):
    trips: TripRepository
    preferences: PreferenceRepository
    places: PlaceRepository
    interest_regions: InterestRegionRepository
    users: UserRepository
    health: HealthRepository


class SQLAlchemyUnitOfWork:
    def __init__(self, session: Session) -> None:
        self._session = session
        self.trips = PostgreSQLTripRepository(session)
        self.preferences = PostgreSQLPreferenceRepository(session)
        self.places = PostgreSQLPlaceRepository(session)
        self.interest_regions = PostgreSQLInterestRegionRepository(session)
        self.users = PostgreSQLUserRepository(session)
        self.health = PostgreSQLHealthRepository(session)


def get_uow() -> Generator[UnitOfWork, None, None]:
    session = SessionLocal()
    try:
        yield SQLAlchemyUnitOfWork(session)
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
