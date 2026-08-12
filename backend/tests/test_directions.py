import pytest
from fastapi.testclient import TestClient
from sqlalchemy.exc import SQLAlchemyError

from conftest import FakeUow

PLACE_ID = "30000000-0000-0000-0000-000000000001"
REQUEST_BODY = {
    "place_id": PLACE_ID,
    "origin": {
        "latitude": 37.5034,
        "longitude": 126.7660,
    },
    "mode": "transit",
}


def test_search_directions_returns_mock_route(client: TestClient) -> None:
    response = client.post("/api/v1/directions/search", json=REQUEST_BODY)

    assert response.status_code == 200
    route = response.json()["data"]["routes"][0]
    assert route["provider"] == "mock"
    assert route["mode"] == "transit"
    assert route["destination"] == {
        "latitude": 37.5,
        "longitude": 127.0,
        "place_id": PLACE_ID,
        "name": "공원",
    }
    assert route["summary"]["distance_meters"] > 0
    assert route["summary"]["duration_seconds"] > 0
    assert route["geometry"]["type"] == "LineString"
    coordinates = route["geometry"]["coordinates"]
    assert coordinates[0] == [126.766, 37.5034]
    assert coordinates[-1] == [127.0, 37.5]
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
    fake_uow: FakeUow,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fail_to_get_place(place_id: object) -> None:
        raise SQLAlchemyError("database unavailable")

    monkeypatch.setattr(fake_uow.places, "get", fail_to_get_place)
    response = client.post("/api/v1/directions/search", json=REQUEST_BODY)

    assert response.status_code == 500
    assert response.json() == {"detail": "Unknown place data error"}
