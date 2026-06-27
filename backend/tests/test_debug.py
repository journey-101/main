from fastapi.testclient import TestClient

from app.main import app


def test_debug_test_user_returns_fixed_user_id() -> None:
    client = TestClient(app)

    response = client.get("/api/v1/debug/test-user")

    assert response.status_code == 200
    assert response.json() == {
        "success": True,
        "data": {
            "user_id": "00000000-0000-0000-0000-000000000000",
        },
    }
