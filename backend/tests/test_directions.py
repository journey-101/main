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
REQUEST_BODY = {
    "place_id": PLACE_ID,
    "origin": {
        "latitude": 37.5034,
        "longitude": 126.7660,
    },
    "mode": "transit",
}


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
        connection.execute(
            text("""
                insert into places values (
                    :id, 'mock', 'bucheon-001', '한국만화박물관', 'museum',
                    '[]', '경기도 부천시 원미구 길주로 1', 'KR-41',
                    37.5088, 126.742, '{}', 1, null,
                    'https://www.komacon.kr/comicsmuseum'
                )
            """),
            {"id": PLACE_ID},
        )

    def override_db_session() -> Generator[Session, None, None]:
        with session_factory() as session:
            yield session

    app.dependency_overrides[get_db_session] = override_db_session
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def test_search_directions_returns_mock_route(client: TestClient) -> None:
    response = client.post("/api/v1/directions/search", json=REQUEST_BODY)

    assert response.status_code == 200
    route = response.json()["data"]["routes"][0]
    assert route["provider"] == "mock"
    assert route["mode"] == "transit"
    assert route["destination"] == {
        "latitude": 37.5088,
        "longitude": 126.742,
        "place_id": PLACE_ID,
        "name": "한국만화박물관",
    }
    assert route["summary"]["distance_meters"] > 0
    assert route["summary"]["duration_seconds"] > 0
    assert route["geometry"]["type"] == "LineString"
    coordinates = route["geometry"]["coordinates"]
    assert coordinates[0] == [126.766, 37.5034]
    assert coordinates[-1] == [126.742, 37.5088]
    assert len(coordinates) == 5
    assert len({tuple(coordinate) for coordinate in coordinates}) == 5


def test_search_directions_returns_not_found_for_unknown_place(
    client: TestClient,
) -> None:
    body = {
        **REQUEST_BODY,
        "place_id": "30000000-0000-0000-0000-000000000099",
    }
    response = client.post("/api/v1/directions/search", json=body)

    assert response.status_code == 404
    assert response.json() == {"detail": "Place not found"}


@pytest.mark.parametrize(
    "body",
    [
        {**REQUEST_BODY, "mode": "flying"},
        {**REQUEST_BODY, "origin": {"latitude": 91, "longitude": 126.766}},
        {**REQUEST_BODY, "unexpected": True},
    ],
)
def test_search_directions_rejects_invalid_request(
    client: TestClient,
    body: dict[str, object],
) -> None:
    assert client.post("/api/v1/directions/search", json=body).status_code == 422


def test_search_directions_handles_place_database_failure(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fail_to_get_place(session: Session, place_id: object) -> None:
        raise SQLAlchemyError("database unavailable")

    monkeypatch.setattr(repository, "get_place", fail_to_get_place)
    response = client.post("/api/v1/directions/search", json=REQUEST_BODY)

    assert response.status_code == 500
    assert response.json() == {"detail": "Unknown place data error"}
