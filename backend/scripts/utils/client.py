from __future__ import annotations

import json
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


class ApiError(RuntimeError):
    pass


class ApiClient:
    def __init__(
        self, base_url: str, timeout: float = 10.0, bearer_token: str | None = None
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.bearer_token = bearer_token

    def get(
        self,
        path: str,
        *,
        query: dict[str, str] | None = None,
        expected_status: int = 200,
    ) -> dict[str, Any]:
        return self.request("GET", path, query=query, expected_status=expected_status)

    def post(
        self,
        path: str,
        *,
        payload: dict[str, Any],
        expected_status: int = 200,
    ) -> dict[str, Any]:
        return self.request(
            "POST", path, payload=payload, expected_status=expected_status
        )

    def patch(
        self,
        path: str,
        *,
        payload: dict[str, Any],
        expected_status: int = 200,
    ) -> dict[str, Any]:
        return self.request(
            "PATCH", path, payload=payload, expected_status=expected_status
        )

    def request(
        self,
        method: str,
        path: str,
        *,
        query: dict[str, str] | None = None,
        payload: dict[str, Any] | None = None,
        expected_status: int = 200,
    ) -> dict[str, Any]:
        url = self._url(path, query)
        body = None
        headers = {"Accept": "application/json"}
        if self.bearer_token:
            headers["Authorization"] = f"Bearer {self.bearer_token}"
        if payload is not None:
            body = json.dumps(payload).encode("utf-8")
            headers["Content-Type"] = "application/json"

        request = Request(url, data=body, headers=headers, method=method)
        try:
            with urlopen(request, timeout=self.timeout) as response:
                response_body = response.read().decode("utf-8")
                status = response.status
        except HTTPError as exc:
            response_body = exc.read().decode("utf-8")
            raise ApiError(
                f"{method} {url} returned {exc.code}, expected {expected_status}: {response_body}"
            ) from exc
        except URLError as exc:
            raise ApiError(f"{method} {url} failed: {exc.reason}") from exc
        except OSError as exc:
            raise ApiError(f"{method} {url} failed: {exc}") from exc

        if status != expected_status:
            raise ApiError(
                f"{method} {url} returned {status}, expected {expected_status}: {response_body}"
            )

        try:
            data = json.loads(response_body)
        except json.JSONDecodeError as exc:
            raise ApiError(
                f"{method} {url} returned invalid JSON: {response_body}"
            ) from exc

        return data

    def _url(self, path: str, query: dict[str, str] | None) -> str:
        normalized_path = path if path.startswith("/") else f"/{path}"
        url = f"{self.base_url}{normalized_path}"
        if query:
            url = f"{url}?{urlencode(query)}"
        return url
