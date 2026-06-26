from collections.abc import Generator
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.session import get_db_session
from app.main import app

USER_ID = "00000000-0000-0000-0000-000000000000"
TRIP_ID = "10000000-0000-0000-0000-000000000001"
OTHER_TRIP_ID = "10000000-0000-0000-0000-000000000002"
ATTEMPT_ID = "20000000-0000-0000-0000-000000000001"
OTHER_ATTEMPT_ID = "20000000-0000-0000-0000-000000000002"


@pytest.fixture()
def client() -> Generator[TestClient, None, None]:
    engine = create_engine(
        "sqlite+pysqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    session_factory = sessionmaker(bind=engine, autoflush=False, autocommit=False)

    with engine.begin() as connection:
        connection.execute(text("create table app_users (id text primary key)"))
        connection.execute(
            text(
                """
                create table trips (
                    id text primary key,
                    user_id text not null references app_users(id),
                    title text not null
                )
                """
            )
        )
        connection.execute(
            text(
                """
                create table trip_attempts (
                    id text primary key,
                    trip_id text not null references trips(id),
                    status text not null,
                    feedback_text text,
                    created_at timestamp not null default current_timestamp
                )
                """
            )
        )
        connection.execute(text("insert into app_users (id) values (:id)"), {"id": USER_ID})
        connection.execute(
            text("insert into trips (id, user_id, title) values (:id, :user_id, :title)"),
            {"id": TRIP_ID, "user_id": USER_ID, "title": "북촌 산책"},
        )
        connection.execute(
            text("insert into trips (id, user_id, title) values (:id, :user_id, :title)"),
            {"id": OTHER_TRIP_ID, "user_id": USER_ID, "title": "성수 탐방"},
        )
        connection.execute(
            text(
                """
                insert into trip_attempts (id, trip_id, status, feedback_text, created_at)
                values (:id, :trip_id, :status, :feedback_text, :created_at)
                """
            ),
            {
                "id": ATTEMPT_ID,
                "trip_id": TRIP_ID,
                "status": "started",
                "feedback_text": None,
                "created_at": "2026-01-01 00:00:00",
            },
        )
        connection.execute(
            text(
                """
                insert into trip_attempts (id, trip_id, status, feedback_text, created_at)
                values (:id, :trip_id, :status, :feedback_text, :created_at)
                """
            ),
            {
                "id": OTHER_ATTEMPT_ID,
                "trip_id": OTHER_TRIP_ID,
                "status": "completed",
                "feedback_text": "좋았다.",
                "created_at": "2026-01-02 00:00:00",
            },
        )

    def override_db_session() -> Generator[Session, None, None]:
        session = session_factory()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db_session] = override_db_session
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def test_get_trips_returns_user_trip_list(client: TestClient) -> None:
    response = client.get(f"/api/v1/trips?user_id={USER_ID}")

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"] == [
        {
            "id": TRIP_ID,
            "user_id": USER_ID,
            "title": "북촌 산책",
            "current_attempt": {
                "id": ATTEMPT_ID,
                "status": "started",
                "feedback_text": None,
            },
        },
        {
            "id": OTHER_TRIP_ID,
            "user_id": USER_ID,
            "title": "성수 탐방",
            "current_attempt": {
                "id": OTHER_ATTEMPT_ID,
                "status": "completed",
                "feedback_text": "좋았다.",
            },
        },
    ]


def test_post_trip_creates_trip_and_started_attempt(client: TestClient) -> None:
    response = client.post(
        "/api/v1/trips",
        json={"user_id": USER_ID, "title": "한강 산책"},
    )

    assert response.status_code == 201
    data = response.json()["data"]
    assert data["user_id"] == USER_ID
    assert data["title"] == "한강 산책"
    assert data["current_attempt"]["status"] == "started"
    assert data["current_attempt"]["feedback_text"] is None

    list_response = client.get(f"/api/v1/trips?user_id={USER_ID}")
    titles = {trip["title"] for trip in list_response.json()["data"]}
    assert "한강 산책" in titles


def test_get_trip_returns_detail_with_attempts(client: TestClient) -> None:
    response = client.get(f"/api/v1/trips/{TRIP_ID}")

    assert response.status_code == 200
    assert response.json()["data"] == {
        "id": TRIP_ID,
        "user_id": USER_ID,
        "title": "북촌 산책",
        "attempts": [
            {
                "id": ATTEMPT_ID,
                "trip_id": TRIP_ID,
                "status": "started",
                "feedback_text": None,
                "created_at": "2026-01-01T00:00:00",
            }
        ],
    }


def test_post_trip_attempt_creates_attempt(client: TestClient) -> None:
    response = client.post(
        f"/api/v1/trips/{TRIP_ID}/attempts",
        json={"status": "completed"},
    )

    assert response.status_code == 201
    data = response.json()["data"]
    assert data["trip_id"] == TRIP_ID
    assert data["status"] == "completed"
    assert data["feedback_text"] is None


def test_post_trip_attempt_defaults_to_started(client: TestClient) -> None:
    response = client.post(f"/api/v1/trips/{TRIP_ID}/attempts", json={})

    assert response.status_code == 201
    data = response.json()["data"]
    assert data["trip_id"] == TRIP_ID
    assert data["status"] == "started"
    assert data["feedback_text"] is None


def test_patch_trip_attempt_updates_feedback_text(client: TestClient) -> None:
    response = client.patch(
        f"/api/v1/trips/{TRIP_ID}/attempts/{ATTEMPT_ID}",
        json={"feedback_text": "생각보다 괜찮았다."},
    )

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["trip_id"] == TRIP_ID
    assert data["status"] == "started"
    assert data["feedback_text"] == "생각보다 괜찮았다."


def test_patch_trip_attempt_updates_status(client: TestClient) -> None:
    response = client.patch(
        f"/api/v1/trips/{TRIP_ID}/attempts/{ATTEMPT_ID}",
        json={"status": "aborted"},
    )

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["status"] == "aborted"
    assert data["feedback_text"] is None


def test_patch_trip_attempt_updates_status_and_feedback_text(client: TestClient) -> None:
    response = client.patch(
        f"/api/v1/trips/{TRIP_ID}/attempts/{ATTEMPT_ID}",
        json={"status": "completed", "feedback_text": "완료했다."},
    )

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["status"] == "completed"
    assert data["feedback_text"] == "완료했다."


def test_patch_trip_attempt_feedback_updates_feedback_text_only(client: TestClient) -> None:
    response = client.patch(
        f"/api/v1/trips/{TRIP_ID}/attempts/{ATTEMPT_ID}/feedback",
        json={"feedback_text": "피드백만 수정했다."},
    )

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["id"] == ATTEMPT_ID
    assert data["trip_id"] == TRIP_ID
    assert data["status"] == "started"
    assert data["feedback_text"] == "피드백만 수정했다."


def test_patch_trip_updates_title_only(client: TestClient) -> None:
    response = client.patch(
        f"/api/v1/trips/{TRIP_ID}",
        json={"title": "북촌 야간 산책"},
    )

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["title"] == "북촌 야간 산책"
    assert data["current_attempt"]["id"] == ATTEMPT_ID


def test_invalid_trip_id_returns_validation_error(client: TestClient) -> None:
    response = client.get("/api/v1/trips/not-a-uuid")

    assert response.status_code == 422


def test_invalid_attempt_feedback_body_returns_validation_error(client: TestClient) -> None:
    response = client.patch(
        f"/api/v1/trips/{TRIP_ID}/attempts/{ATTEMPT_ID}",
        json={"feedback_text": 123},
    )

    assert response.status_code == 422


def test_invalid_feedback_only_body_returns_validation_error(client: TestClient) -> None:
    response = client.patch(
        f"/api/v1/trips/{TRIP_ID}/attempts/{ATTEMPT_ID}/feedback",
        json={"feedback_text": 123},
    )

    assert response.status_code == 422


def test_missing_feedback_only_body_returns_validation_error(client: TestClient) -> None:
    response = client.patch(
        f"/api/v1/trips/{TRIP_ID}/attempts/{ATTEMPT_ID}/feedback",
        json={},
    )

    assert response.status_code == 422


def test_feedback_only_body_rejects_extra_fields(client: TestClient) -> None:
    response = client.patch(
        f"/api/v1/trips/{TRIP_ID}/attempts/{ATTEMPT_ID}/feedback",
        json={"feedback_text": "좋았다.", "status": "completed"},
    )

    assert response.status_code == 422


def test_invalid_attempt_status_returns_validation_error(client: TestClient) -> None:
    response = client.post(
        f"/api/v1/trips/{TRIP_ID}/attempts",
        json={"status": "paused"},
    )

    assert response.status_code == 422


def test_empty_attempt_patch_body_returns_validation_error(client: TestClient) -> None:
    response = client.patch(f"/api/v1/trips/{TRIP_ID}/attempts/{ATTEMPT_ID}", json={})

    assert response.status_code == 422


def test_invalid_attempt_patch_body_type_returns_validation_error(client: TestClient) -> None:
    response = client.patch(
        f"/api/v1/trips/{TRIP_ID}/attempts/{ATTEMPT_ID}",
        json=["feedback"],
    )

    assert response.status_code == 422


def test_removed_feedback_route_returns_not_found(client: TestClient) -> None:
    response = client.patch(
        f"/api/v1/trips/{TRIP_ID}/feedback",
        json={"feedback_text": "생각보다 괜찮았다."},
    )

    assert response.status_code == 404


def test_patch_trip_rejects_feedback_alias(client: TestClient) -> None:
    response = client.patch(
        f"/api/v1/trips/{TRIP_ID}",
        json={"feedback_text": "다시 가고 싶다."},
    )

    assert response.status_code == 422


def test_get_missing_trip_returns_not_found(client: TestClient) -> None:
    response = client.get(f"/api/v1/trips/{uuid4()}")

    assert response.status_code == 404
    assert response.json() == {"detail": "Trip not found"}


def test_post_attempt_for_missing_trip_returns_not_found(client: TestClient) -> None:
    response = client.post(f"/api/v1/trips/{uuid4()}/attempts", json={})

    assert response.status_code == 404
    assert response.json() == {"detail": "Trip not found"}


def test_patch_attempt_for_missing_trip_returns_not_found(client: TestClient) -> None:
    response = client.patch(
        f"/api/v1/trips/{uuid4()}/attempts/{ATTEMPT_ID}",
        json={"feedback_text": "없는 여행"},
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Trip not found"}


def test_patch_attempt_feedback_for_missing_trip_returns_not_found(client: TestClient) -> None:
    response = client.patch(
        f"/api/v1/trips/{uuid4()}/attempts/{ATTEMPT_ID}/feedback",
        json={"feedback_text": "없는 여행"},
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Trip not found"}


def test_patch_missing_attempt_returns_not_found(client: TestClient) -> None:
    response = client.patch(
        f"/api/v1/trips/{TRIP_ID}/attempts/{uuid4()}",
        json={"feedback_text": "없는 시도"},
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Trip attempt not found"}


def test_patch_missing_attempt_feedback_returns_not_found(client: TestClient) -> None:
    response = client.patch(
        f"/api/v1/trips/{TRIP_ID}/attempts/{uuid4()}/feedback",
        json={"feedback_text": "없는 시도"},
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Trip attempt not found"}


def test_patch_attempt_for_different_trip_returns_not_found(client: TestClient) -> None:
    response = client.patch(
        f"/api/v1/trips/{TRIP_ID}/attempts/{OTHER_ATTEMPT_ID}",
        json={"feedback_text": "다른 여행 시도"},
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Trip attempt not found"}


def test_patch_attempt_feedback_for_different_trip_returns_not_found(client: TestClient) -> None:
    response = client.patch(
        f"/api/v1/trips/{TRIP_ID}/attempts/{OTHER_ATTEMPT_ID}/feedback",
        json={"feedback_text": "다른 여행 시도"},
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Trip attempt not found"}


def test_patch_missing_trip_title_returns_not_found(client: TestClient) -> None:
    response = client.patch(
        f"/api/v1/trips/{uuid4()}",
        json={"title": "없는 여행"},
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Trip not found"}


def test_post_trip_with_missing_user_returns_not_found(client: TestClient) -> None:
    response = client.post(
        "/api/v1/trips",
        json={"user_id": str(uuid4()), "title": "없는 사용자 여행"},
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "User not found"}
