from fastapi.testclient import TestClient

from app.main import app


def test_health_returns_success_response() -> None:
    client = TestClient(app)

    response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json() == {
        "success": True,
        "data": {
            "status": "ok",
            "service": "backend",
        },
    }
