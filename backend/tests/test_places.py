from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.session import get_db_session
from app.domains.places import repository
from app.main import app

PLACE_ID = "30000000-0000-0000-0000-000000000001"

PLACES = [
    (PLACE_ID, "bucheon-001", "한국만화박물관", "museum", '["indoor", "solo_friendly"]', "경기도 부천시 원미구 길주로 1", 37.5088, 126.742, '{"summary": "10:00-18:00"}', 1, "032-310-3090", "https://www.komacon.kr/comicsmuseum"),
    ("30000000-0000-0000-0000-000000000002", "bucheon-002", "상동호수공원", "park", '["outdoor", "walk", "quiet"]', "경기도 부천시 원미구 조마루로 15", 37.5054, 126.7446, '{"summary": "24 hours"}', 0, None, "https://www.bucheon.go.kr"),
    ("30000000-0000-0000-0000-000000000003", "bucheon-003", "부천아트센터", "concert_hall", '["indoor", "culture"]', "경기도 부천시 원미구 소향로 165", 37.5037, 126.7658, '{"summary": "Schedule dependent"}', 2, "1533-0202", "https://www.bac.or.kr"),
]


@pytest.fixture()
def client() -> Generator[TestClient, None, None]:
    engine = create_engine(
        "sqlite+pysqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    session_factory = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    with engine.begin() as connection:
        connection.execute(text("""
            create table places (
                id text primary key, provider text not null,
                provider_place_id text not null, name text not null,
                category text not null, tags text not null, address text not null,
                region_code text not null, lat real not null, lng real not null,
                opening_hours text not null, price_level integer not null,
                phone text, source_url text not null
            )
        """))
        for place in PLACES:
            connection.execute(text("""
                insert into places values (
                    :id, 'mock', :provider_place_id, :name, :category, :tags,
                    :address, 'KR-41', :lat, :lng, :opening_hours,
                    :price_level, :phone, :source_url
                )
            """), dict(zip(("id", "provider_place_id", "name", "category", "tags", "address", "lat", "lng", "opening_hours", "price_level", "phone", "source_url"), place, strict=True)))

    def override_db_session() -> Generator[Session, None, None]:
        with session_factory() as session:
            yield session

    app.dependency_overrides[get_db_session] = override_db_session
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def test_search_places_returns_database_place_list(client: TestClient) -> None:
    response = client.get("/api/v1/places/search")
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"]["next_cursor"] is None
    assert len(body["data"]["items"]) == 3
    assert body["data"]["items"][0] == {
        "id": PLACE_ID, "provider": "mock", "provider_place_id": "bucheon-001",
        "name": "한국만화박물관", "category": "museum",
        "tags": ["indoor", "solo_friendly"], "address": "경기도 부천시 원미구 길주로 1",
        "region_code": "KR-41", "lat": 37.5088, "lng": 126.742,
        "price_level": 1, "source_url": "https://www.komacon.kr/comicsmuseum",
    }


def test_search_places_filters_by_query_and_limit(client: TestClient) -> None:
    response = client.get("/api/v1/places/search", params={"category": "park", "region_code": "KR-41", "limit": 1})
    assert response.status_code == 200
    items = response.json()["data"]["items"]
    assert len(items) == 1
    assert items[0]["name"] == "상동호수공원"


def test_search_places_rejects_incomplete_location_query(client: TestClient) -> None:
    assert client.get("/api/v1/places/search", params={"lat": 37.5, "lng": 126.7}).status_code == 422


def test_get_place_returns_place_detail(client: TestClient) -> None:
    response = client.get(f"/api/v1/places/{PLACE_ID}")
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["id"] == PLACE_ID
    assert data["name"] == "한국만화박물관"
    assert data["opening_hours"] == {"summary": "10:00-18:00"}
    assert data["phone"] == "032-310-3090"


def test_get_place_returns_not_found_for_unknown_id(client: TestClient) -> None:
    response = client.get("/api/v1/places/30000000-0000-0000-0000-000000000099")
    assert response.status_code == 404
    assert response.json() == {"detail": "Place not found"}


def test_get_place_rejects_invalid_uuid(client: TestClient) -> None:
    assert client.get("/api/v1/places/not-a-uuid").status_code == 422


def test_search_places_returns_unknown_error_for_database_failure(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fail_to_list_places(session: Session) -> None:
        raise SQLAlchemyError("database unavailable")

    monkeypatch.setattr(repository, "list_places", fail_to_list_places)
    response = client.get("/api/v1/places/search")
    assert response.status_code == 500
    assert response.json() == {"detail": "Unknown place data error"}
