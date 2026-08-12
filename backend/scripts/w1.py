#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

from utils import ApiClient, ApiError, load_payload


SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_BASE_URL = os.environ.get("BACKEND_BASE_URL", "http://localhost:8000")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run the w1 end-to-end trip attempt feedback flow against a local backend."
    )
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    parser.add_argument("--data-dir", type=Path, default=SCRIPT_DIR / "data")
    parser.add_argument("--timeout", type=float, default=10.0)
    parser.add_argument(
        "--token",
        default=os.environ.get("FIREBASE_ID_TOKEN"),
        help="Firebase ID token (or set FIREBASE_ID_TOKEN)",
    )
    args = parser.parse_args()
    if not args.token:
        parser.error("--token or FIREBASE_ID_TOKEN is required")

    client = ApiClient(args.base_url, timeout=args.timeout, bearer_token=args.token)
    run_id = f"{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}-{uuid4().hex[:8]}"

    try:
        run_flow(client, args.data_dir, run_id)
    except (ApiError, AssertionError, KeyError, ValueError) as exc:
        print(f"[fail] {exc}")
        return 1

    print("[ok] w1 flow validation completed")
    return 0


def run_flow(client: ApiClient, data_dir: Path, run_id: str) -> None:
    print("[step] verify Firebase user")
    expect_success(client.get("/api/v1/auth/me"))
    context = {"run_id": run_id}

    print("[step] create trip")
    create_trip_payload = load_payload(data_dir, "create_trip.json", context)
    created_trip = expect_success(
        client.post("/api/v1/trips", payload=create_trip_payload, expected_status=201)
    )
    trip_id = created_trip["id"]
    assert_equal(
        created_trip["title"], create_trip_payload["title"], "created trip title"
    )
    assert_equal(
        created_trip["current_attempt"]["status"], "started", "default attempt status"
    )

    print("[step] confirm trip in list")
    listed_trips = expect_success(client.get("/api/v1/trips"))
    matching_trip = find_by_id(listed_trips, trip_id)
    assert_equal(
        matching_trip["title"], create_trip_payload["title"], "listed trip title"
    )

    print("[step] load trip detail")
    trip_detail = expect_success(client.get(f"/api/v1/trips/{trip_id}"))
    assert_equal(trip_detail["id"], trip_id, "trip detail id")
    assert any(
        attempt["id"] == created_trip["current_attempt"]["id"]
        for attempt in trip_detail["attempts"]
    ), "created default attempt not found in detail"

    print("[step] create attempt")
    create_attempt_payload = load_payload(data_dir, "create_attempt.json", context)
    created_attempt = expect_success(
        client.post(
            f"/api/v1/trips/{trip_id}/attempts",
            payload=create_attempt_payload,
            expected_status=201,
        )
    )
    attempt_id = created_attempt["id"]
    assert_equal(created_attempt["trip_id"], trip_id, "created attempt trip_id")
    assert_equal(
        created_attempt["status"],
        create_attempt_payload["status"],
        "created attempt status",
    )

    print("[step] confirm attempt in trip detail")
    trip_detail = expect_success(client.get(f"/api/v1/trips/{trip_id}"))
    matching_attempt = find_by_id(trip_detail["attempts"], attempt_id)
    assert_equal(
        matching_attempt["status"],
        create_attempt_payload["status"],
        "detail attempt status",
    )

    print("[step] update attempt feedback")
    update_feedback_payload = load_payload(data_dir, "update_feedback.json", context)
    updated_attempt = expect_success(
        client.patch(
            f"/api/v1/trips/{trip_id}/attempts/{attempt_id}/feedback",
            payload=update_feedback_payload,
        )
    )
    assert_equal(updated_attempt["id"], attempt_id, "updated attempt id")
    assert_equal(
        updated_attempt["feedback_text"],
        update_feedback_payload["feedback_text"],
        "updated feedback_text",
    )

    print("[step] confirm feedback in trip detail")
    trip_detail = expect_success(client.get(f"/api/v1/trips/{trip_id}"))
    matching_attempt = find_by_id(trip_detail["attempts"], attempt_id)
    assert_equal(
        matching_attempt["feedback_text"],
        update_feedback_payload["feedback_text"],
        "detail feedback_text",
    )


def expect_success(response: dict[str, Any]) -> Any:
    assert response.get("success") is True, f"response success was not true: {response}"
    return response["data"]


def find_by_id(items: list[dict[str, Any]], item_id: str) -> dict[str, Any]:
    for item in items:
        if item.get("id") == item_id:
            return item
    raise AssertionError(f"id {item_id} not found in response list")


def assert_equal(actual: Any, expected: Any, label: str) -> None:
    assert actual == expected, f"{label}: expected {expected!r}, got {actual!r}"


if __name__ == "__main__":
    raise SystemExit(main())
