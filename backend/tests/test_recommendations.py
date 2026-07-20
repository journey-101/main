from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.session import get_db_session
from app.main import app

USER_ID = "00000000-0000-0000-0000-000000000000"
OTHER_USER_ID = "00000000-0000-0000-0000-000000000099"
TRIP_ID = "10000000-0000-0000-0000-000000000001"


@pytest.fixture()
def client() -> Generator[TestClient, None, None]:
    engine = create_engine("sqlite+pysqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    session_factory = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    with engine.begin() as connection:
        connection.execute(text("create table app_users (id text primary key)"))
        connection.execute(text("create table trips (id text primary key, user_id text not null, title text not null)"))
        connection.execute(text("create table trip_attempts (id text primary key, trip_id text not null, status text not null, feedback_text text, created_at timestamp)"))
        connection.execute(text("create table user_preferences (user_id text primary key, preferred_categories text not null, avoided_categories text not null, prefers_quiet boolean not null, max_walk_minutes integer not null, is_first_time_traveler boolean not null, updated_at timestamp default current_timestamp)"))
        connection.execute(text("insert into app_users (id) values (:id), (:other_id)"), {"id": USER_ID, "other_id": OTHER_USER_ID})
        connection.execute(text("insert into trips (id, user_id, title) values (:id, :user_id, :title)"), {"id": TRIP_ID, "user_id": USER_ID, "title": "북촌 산책"})
        connection.execute(text("insert into user_preferences (user_id, preferred_categories, avoided_categories, prefers_quiet, max_walk_minutes, is_first_time_traveler) values (:user_id, :preferred, :avoided, :quiet, :walk, :first_time)"), {"user_id": USER_ID, "preferred": '[\"museum\", \"park\"]', "avoided": '[\"concert_hall\"]', "quiet": True, "walk": 20, "first_time": True})

    def override_db_session() -> Generator[Session, None, None]:
        session = session_factory()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    app.dependency_overrides[get_db_session] = override_db_session
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def preference_payload(**changes: object) -> dict[str, object]:
    payload: dict[str, object] = {"user_id": USER_ID, "preferred_categories": ["museum", "park"], "avoided_categories": ["concert_hall"], "prefers_quiet": True, "max_walk_minutes": 20, "is_first_time_traveler": True}
    payload.update(changes)
    return payload


def test_get_preferences_and_missing_states(client: TestClient) -> None:
    assert client.get("/api/v1/me/preferences", params={"user_id": USER_ID}).status_code == 200
    assert client.get("/api/v1/me/preferences", params={"user_id": "10000000-0000-0000-0000-000000000099"}).json() == {"detail": "User not found"}
    response = client.get("/api/v1/me/preferences", params={"user_id": OTHER_USER_ID})
    assert response.status_code == 404
    assert response.json() == {"detail": "User preference not found"}


def test_put_preferences_creates_updates_and_validates(client: TestClient) -> None:
    new_user = "00000000-0000-0000-0000-000000000098"
    created = client.put("/api/v1/me/preferences", json=preference_payload(user_id=OTHER_USER_ID))
    assert created.status_code == 200
    response = client.put("/api/v1/me/preferences", json=preference_payload(preferred_categories=["park"]))
    assert response.status_code == 200
    assert response.json()["data"]["preferred_categories"] == ["park"]
    assert client.get("/api/v1/me/preferences", params={"user_id": USER_ID}).json()["data"]["preferred_categories"] == ["park"]
    assert client.put("/api/v1/me/preferences", json=preference_payload(user_id=new_user)).json() == {"detail": "User not found"}
    assert client.put("/api/v1/me/preferences", json={"user_id": USER_ID}).status_code == 422
    assert client.put("/api/v1/me/preferences", json=preference_payload(extra=True)).status_code == 422
    assert client.put("/api/v1/me/preferences", json=preference_payload(max_walk_minutes=0)).status_code == 422


def test_place_recommendation_is_deterministic_and_convenience_matches(client: TestClient) -> None:
    request = {"user_id": USER_ID, "method": "preference_mock", "target": {"type": "place", "region_code": "KR-41"}, "limit": 10}
    first = client.post("/api/v1/recommendations", json=request)
    second = client.post("/api/v1/recommendations", json=request)
    convenience = client.post("/api/v1/recommendations/places", json={"user_id": USER_ID, "region_code": "KR-41", "limit": 10})
    assert first.status_code == 200
    assert first.json()["data"]["fallback"]["used"] is False
    assert first.json()["data"]["items"] == second.json()["data"]["items"] == convenience.json()["data"]["items"]
    client.put("/api/v1/me/preferences", json=preference_payload(preferred_categories=["museum"], max_walk_minutes=10))
    changed = client.post("/api/v1/recommendations", json=request)
    assert changed.json()["data"]["items"] != first.json()["data"]["items"]


def test_trip_recommendation_fallback_and_errors(client: TestClient) -> None:
    request = {"user_id": USER_ID, "method": "preference_mock", "target": {"type": "trip", "trip_id": TRIP_ID}, "limit": 10}
    common = client.post("/api/v1/recommendations", json=request)
    convenience = client.post("/api/v1/recommendations/trips", json={"user_id": USER_ID, "trip_id": TRIP_ID, "limit": 10})
    assert common.json()["data"]["fallback"] == {"used": True, "reason": "trip_place_not_available", "fallback_target": {"type": "place"}}
    assert common.json()["data"]["items"] == convenience.json()["data"]["items"]
    assert client.post("/api/v1/recommendations", json={**request, "method": "unknown"}).status_code == 422
    assert client.post("/api/v1/recommendations", json={**request, "target": {"type": "unknown"}}).status_code == 422
    assert client.post("/api/v1/recommendations", json={**request, "target": {"type": "trip", "trip_id": "10000000-0000-0000-0000-000000000099"}}).json() == {"detail": "Trip not found"}
    client.put("/api/v1/me/preferences", json=preference_payload(user_id=OTHER_USER_ID))
    assert client.post("/api/v1/recommendations", json={**request, "user_id": OTHER_USER_ID}).json() == {"detail": "Trip not found"}
