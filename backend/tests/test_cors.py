import httpx
import pytest
from httpx import ASGITransport

from app.main import app


@pytest.fixture()
def anyio_backend() -> str:
    return "asyncio"


@pytest.mark.anyio
async def test_cors_preflight_allows_configured_frontend_origin() -> None:
    async with httpx.AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        response = await client.options(
            "/api/v1/health",
            headers={
                "Origin": "http://localhost:5173",
                "Access-Control-Request-Method": "GET",
                "Access-Control-Request-Headers": "Accept, Authorization, Content-Type",
            },
        )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:5173"
    allowed_methods = response.headers["access-control-allow-methods"]
    assert all(
        method in allowed_methods
        for method in ("GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH")
    )
    allow_headers = response.headers["access-control-allow-headers"]
    assert "Accept" in allow_headers
    assert "Authorization" in allow_headers
    assert "Content-Type" in allow_headers
    assert "access-control-allow-credentials" not in response.headers


@pytest.mark.anyio
async def test_cors_simple_request_sets_allow_origin_header() -> None:
    async with httpx.AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        response = await client.get(
            "/api/v1/health",
            headers={"Origin": "http://127.0.0.1:5173"},
        )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://127.0.0.1:5173"
    assert "access-control-allow-credentials" not in response.headers
