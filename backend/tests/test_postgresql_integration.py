import os
from datetime import UTC, datetime
from uuid import UUID, uuid4

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session

from app.domains.places.postgresql import PostgreSQLPlaceRepository
from app.domains.places.repository import PlaceSearch
from app.domains.regions.postgresql import PostgreSQLInterestRegionRepository
from app.domains.trips.postgresql import PostgreSQLTripRepository

DATABASE_URL = os.getenv("TEST_DATABASE_URL")
pytestmark = pytest.mark.skipif(not DATABASE_URL, reason="TEST_DATABASE_URL is not set")


@pytest.fixture()
def session() -> Session:
    engine = create_engine(DATABASE_URL)
    connection = engine.connect()
    transaction = connection.begin()
    value = Session(bind=connection)
    try:
        yield value
    finally:
        value.close()
        transaction.rollback()
        connection.close()
        engine.dispose()


def test_postgis_radius_boundary_and_gist_index(session: Session) -> None:
    places = PostgreSQLPlaceRepository(session).search(
        PlaceSearch(category="park", lat=37.5054, lng=126.7446, radius_m=500, limit=10)
    )
    assert [place.name for place in places] == ["상동호수공원"]
    boundary = session.execute(
        text("""
        select ST_Covers(boundary, ST_SetSRID(ST_Point(126, 37), 4326)),
               ST_Contains(boundary, ST_SetSRID(ST_Point(126, 37), 4326))
        from regions where code = 'KR-41'
    """)
    ).one()
    assert boundary == (True, False)
    session.execute(text("set local enable_seqscan = off"))
    plan = "\n".join(
        session.execute(
            text("""
        explain select id from places where ST_DWithin(
          location, ST_SetSRID(ST_MakePoint(126.742,37.5088),4326)::geography, 1000
        )
    """)
        ).scalars()
    )
    assert "ix_places_location_gist" in plan


def test_interest_regions_replace_is_atomic_repository_operation(
    session: Session,
) -> None:
    uid = f"integration-{uuid4()}"
    region_id = session.execute(
        text("select id from regions where code = 'KR-41'")
    ).scalar_one()
    session.execute(
        text("insert into app_users(firebase_uid) values (:uid)"), {"uid": uid}
    )
    repository = PostgreSQLInterestRegionRepository(session)
    repository.replace_for_user(uid, [region_id, region_id])
    assert [region.id for region in repository.list_for_user(uid)] == [region_id]
    repository.replace_for_user(uid, [])
    assert repository.list_for_user(uid) == []


def test_latest_attempt_uses_created_at_then_id_desc(session: Session) -> None:
    uid = f"integration-{uuid4()}"
    trip_id = uuid4()
    low_id = UUID("50000000-0000-0000-0000-000000000001")
    high_id = UUID("50000000-0000-0000-0000-000000000002")
    created_at = datetime(2026, 1, 1, tzinfo=UTC)
    session.execute(
        text("insert into app_users(firebase_uid) values (:uid)"), {"uid": uid}
    )
    session.execute(
        text("insert into trips(id, firebase_uid, title) values (:id, :uid, 'tie')"),
        {"id": trip_id, "uid": uid},
    )
    for attempt_id, status in ((low_id, "started"), (high_id, "completed")):
        session.execute(
            text("""
            insert into trip_attempts(id, trip_id, status, created_at)
            values (:id, :trip_id, :status, :created_at)
        """),
            {
                "id": attempt_id,
                "trip_id": trip_id,
                "status": status,
                "created_at": created_at,
            },
        )
    current = PostgreSQLTripRepository(session).current_attempt(trip_id, uid)
    assert current is not None
    assert current.id == high_id
