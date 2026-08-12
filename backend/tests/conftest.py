from collections.abc import Generator
from datetime import UTC, datetime
from uuid import UUID

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

from app.core.auth import CurrentUser, TokenVerifier, get_token_verifier
from app.db.uow import get_uow
from app.domains.places.repository import PlaceRecord, PlaceSearch
from app.domains.recommendations.repository import PreferenceRecord
from app.domains.trips.repository import AttemptRecord, TripListRecord, TripRecord
from app.domains.trips.schemas import TripAttemptStatus
from app.main import app

TRIP_ID = UUID("10000000-0000-0000-0000-000000000001")
ATTEMPT_ID = UUID("20000000-0000-0000-0000-000000000001")
PLACE_ID = UUID("30000000-0000-0000-0000-000000000001")


class FakeVerifier(TokenVerifier):
    def verify(self, token: str) -> CurrentUser:
        if token == "valid-a":
            return CurrentUser("uid-a", "a@example.com", "A", "google.com")
        if token == "valid-b":
            return CurrentUser("uid-b", "b@example.com", "B", "google.com")
        raise HTTPException(
            status_code=401, detail="Invalid or missing Firebase ID token"
        )


class FakeUsers:
    def __init__(self) -> None:
        self.uids: set[str] = set()

    def ensure(self, firebase_uid: str) -> None:
        self.uids.add(firebase_uid)


class FakeTrips:
    def __init__(self) -> None:
        self.trip = TripRecord(TRIP_ID, "uid-a", "북촌 산책")
        self.attempt = AttemptRecord(
            ATTEMPT_ID,
            TRIP_ID,
            TripAttemptStatus.started,
            None,
            datetime(2026, 1, 1, tzinfo=UTC),
        )

    def list_for_user(self, uid: str) -> list[TripListRecord]:
        return (
            [TripListRecord(self.trip, self.attempt)]
            if uid == self.trip.firebase_uid
            else []
        )

    def get(self, trip_id: UUID, uid: str) -> TripRecord | None:
        return (
            self.trip if trip_id == TRIP_ID and uid == self.trip.firebase_uid else None
        )

    def attempts(self, trip_id: UUID, uid: str) -> list[AttemptRecord]:
        return [self.attempt] if self.get(trip_id, uid) else []

    def current_attempt(self, trip_id: UUID, uid: str) -> AttemptRecord | None:
        return self.attempt if self.get(trip_id, uid) else None

    def create_with_attempt(
        self, uid: str, title: str
    ) -> tuple[TripRecord, AttemptRecord]:
        self.trip = TripRecord(TRIP_ID, uid, title)
        return self.trip, self.attempt

    def update_title(self, trip_id: UUID, uid: str, title: str) -> TripRecord | None:
        if not self.get(trip_id, uid):
            return None
        self.trip = TripRecord(TRIP_ID, uid, title)
        return self.trip

    def create_attempt(
        self, trip_id: UUID, uid: str, status: TripAttemptStatus
    ) -> AttemptRecord | None:
        if not self.get(trip_id, uid):
            return None
        self.attempt = AttemptRecord(
            ATTEMPT_ID, TRIP_ID, status, None, datetime.now(UTC)
        )
        return self.attempt

    def update_attempt(
        self,
        trip_id: UUID,
        attempt_id: UUID,
        uid: str,
        status: TripAttemptStatus | None,
        feedback_text: str | None,
    ) -> AttemptRecord | None:
        if attempt_id != ATTEMPT_ID or not self.get(trip_id, uid):
            return None
        self.attempt = AttemptRecord(
            ATTEMPT_ID,
            TRIP_ID,
            status or self.attempt.status,
            feedback_text if feedback_text is not None else self.attempt.feedback_text,
            self.attempt.created_at,
        )
        return self.attempt


class FakePreferences:
    def __init__(self) -> None:
        self.records: dict[str, PreferenceRecord] = {}

    def get(self, uid: str) -> PreferenceRecord | None:
        return self.records.get(uid)

    def save(self, preference: PreferenceRecord) -> PreferenceRecord:
        self.records[preference.firebase_uid] = preference
        return preference


class FakePlaces:
    place = PlaceRecord(
        PLACE_ID,
        "mock",
        "one",
        "공원",
        "park",
        ["quiet"],
        "서울",
        "KR-11",
        37.5,
        127.0,
        {},
        0,
        None,
        "https://example.com",
    )

    def search(self, query: PlaceSearch) -> list[PlaceRecord]:
        if query.category and query.category != self.place.category:
            return []
        return [self.place][: query.limit]

    def get(self, place_id: UUID) -> PlaceRecord | None:
        return self.place if place_id == PLACE_ID else None


class FakeInterestRegions:
    def list_for_user(self, firebase_uid: str) -> list[object]:
        return []

    def replace_for_user(self, firebase_uid: str, region_ids: list[UUID]) -> None:
        return None


class FakeUow:
    def __init__(self) -> None:
        self.users = FakeUsers()
        self.trips = FakeTrips()
        self.preferences = FakePreferences()
        self.places = FakePlaces()
        self.interest_regions = FakeInterestRegions()
        self.health = self

    def ping(self) -> int:
        return 1


@pytest.fixture()
def fake_uow() -> FakeUow:
    return FakeUow()


@pytest.fixture()
def client(fake_uow: FakeUow) -> Generator[TestClient, None, None]:
    app.dependency_overrides[get_uow] = lambda: fake_uow
    app.dependency_overrides[get_token_verifier] = lambda: FakeVerifier()
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
