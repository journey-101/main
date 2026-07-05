from pathlib import Path

from fastapi.testclient import TestClient

from app.domains.places import service
from app.main import app

PLACE_ID = "30000000-0000-0000-0000-000000000001"


def test_search_places_returns_mock_place_list() -> None:
    client = TestClient(app)

    response = client.get("/api/v1/places/search")

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"]["next_cursor"] is None
    assert len(body["data"]["items"]) == 3
    assert body["data"]["items"][0] == {
        "id": PLACE_ID,
        "provider": "mock",
        "provider_place_id": "bucheon-001",
        "name": "한국만화박물관",
        "category": "museum",
        "tags": ["indoor", "solo_friendly"],
        "address": "경기도 부천시 원미구 길주로 1",
        "region_code": "KR-41",
        "lat": 37.5088,
        "lng": 126.742,
        "price_level": 1,
        "source_url": "https://www.komacon.kr/comicsmuseum",
    }


def test_search_places_filters_by_query_and_limit() -> None:
    client = TestClient(app)

    response = client.get(
        "/api/v1/places/search",
        params={"category": "park", "region_code": "KR-41", "limit": 1},
    )

    assert response.status_code == 200
    items = response.json()["data"]["items"]
    assert len(items) == 1
    assert items[0]["name"] == "상동호수공원"


def test_search_places_rejects_incomplete_location_query() -> None:
    client = TestClient(app)

    response = client.get(
        "/api/v1/places/search",
        params={"lat": 37.5, "lng": 126.7},
    )

    assert response.status_code == 422


def test_get_place_returns_place_detail() -> None:
    client = TestClient(app)

    response = client.get(f"/api/v1/places/{PLACE_ID}")

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["id"] == PLACE_ID
    assert data["name"] == "한국만화박물관"
    assert data["opening_hours"] == {"summary": "10:00-18:00"}
    assert data["phone"] == "032-310-3090"


def test_get_place_returns_not_found_for_unknown_id() -> None:
    client = TestClient(app)

    response = client.get(
        "/api/v1/places/30000000-0000-0000-0000-000000000099"
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Place not found"}


def test_get_place_rejects_invalid_uuid() -> None:
    client = TestClient(app)

    response = client.get("/api/v1/places/not-a-uuid")

    assert response.status_code == 422


def test_search_places_returns_unknown_error_for_invalid_data(
    monkeypatch,
    tmp_path: Path,
) -> None:
    invalid_data_file = tmp_path / "places.json"
    invalid_data_file.write_text("not-json", encoding="utf-8")
    monkeypatch.setattr(service, "DATA_FILE", invalid_data_file)
    client = TestClient(app, raise_server_exceptions=False)

    response = client.get("/api/v1/places/search")

    assert response.status_code == 500
    assert response.json() == {"detail": "Unknown place data error"}
