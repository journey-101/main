from fastapi.testclient import TestClient

from conftest import TRIP_ID, FakeUow


def auth(token: str = "valid-a") -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def test_auth_me_returns_verified_claims_and_projects_user(
    client: TestClient, fake_uow: FakeUow
) -> None:
    response = client.get("/api/v1/auth/me", headers=auth())
    assert response.status_code == 200
    assert response.json()["data"] == {
        "uid": "uid-a",
        "email": "a@example.com",
        "name": "A",
        "provider": "google.com",
    }
    assert fake_uow.users.uids == {"uid-a"}


def test_missing_and_invalid_tokens_are_unauthorized(client: TestClient) -> None:
    assert client.get("/api/v1/trips").status_code == 401
    assert client.get("/api/v1/trips", headers=auth("tampered")).status_code == 401
    assert (
        client.get("/api/v1/me/preferences", headers=auth("expired")).status_code == 401
    )


def test_uid_is_not_accepted_in_trip_contract(client: TestClient) -> None:
    created = client.post("/api/v1/trips", headers=auth(), json={"title": "한강 산책"})
    assert created.status_code == 201
    assert "user_id" not in created.json()["data"]
    assert (
        client.post(
            "/api/v1/trips", headers=auth(), json={"title": "x", "user_id": "uid-b"}
        ).status_code
        == 422
    )


def test_other_user_cannot_access_or_mutate_trip(client: TestClient) -> None:
    assert (
        client.get(f"/api/v1/trips/{TRIP_ID}", headers=auth("valid-b")).status_code
        == 404
    )
    assert (
        client.patch(
            f"/api/v1/trips/{TRIP_ID}", headers=auth("valid-b"), json={"title": "steal"}
        ).status_code
        == 404
    )
    assert (
        client.post(
            f"/api/v1/trips/{TRIP_ID}/attempts", headers=auth("valid-b"), json={}
        ).status_code
        == 404
    )


def test_preferences_use_token_uid_only(client: TestClient, fake_uow: FakeUow) -> None:
    payload = {
        "preferred_categories": ["park"],
        "avoided_categories": [],
        "prefers_quiet": True,
        "max_walk_minutes": 10,
        "is_first_time_traveler": True,
    }
    response = client.put("/api/v1/me/preferences", headers=auth(), json=payload)
    assert response.status_code == 200
    assert "user_id" not in response.json()["data"]
    assert "uid-a" in fake_uow.preferences.records
    assert (
        client.put(
            "/api/v1/me/preferences",
            headers=auth(),
            json={**payload, "user_id": "uid-b"},
        ).status_code
        == 422
    )


def test_places_and_health_remain_public(client: TestClient) -> None:
    assert client.get("/api/v1/places/search").status_code == 200
    assert client.get("/api/v1/health").status_code == 200
