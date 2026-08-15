from dataclasses import dataclass
from datetime import datetime
from typing import Protocol
from uuid import UUID

from app.domains.trips.schemas import TripAttemptStatus


@dataclass(frozen=True)
class TripRecord:
    id: UUID
    firebase_uid: str
    title: str


@dataclass(frozen=True)
class AttemptRecord:
    id: UUID
    trip_id: UUID
    status: TripAttemptStatus
    feedback_text: str | None
    created_at: datetime


@dataclass(frozen=True)
class TripListRecord:
    trip: TripRecord
    current_attempt: AttemptRecord | None


class TripRepository(Protocol):
    def list_for_user(self, firebase_uid: str) -> list[TripListRecord]: ...
    def get(self, trip_id: UUID, firebase_uid: str) -> TripRecord | None: ...
    def attempts(self, trip_id: UUID, firebase_uid: str) -> list[AttemptRecord]: ...
    def current_attempt(
        self, trip_id: UUID, firebase_uid: str
    ) -> AttemptRecord | None: ...
    def create_with_attempt(
        self, firebase_uid: str, title: str
    ) -> tuple[TripRecord, AttemptRecord]: ...
    def update_title(
        self, trip_id: UUID, firebase_uid: str, title: str
    ) -> TripRecord | None: ...
    def create_attempt(
        self, trip_id: UUID, firebase_uid: str, status: TripAttemptStatus
    ) -> AttemptRecord | None: ...
    def update_attempt(
        self,
        trip_id: UUID,
        attempt_id: UUID,
        firebase_uid: str,
        status: TripAttemptStatus | None,
        feedback_text: str | None,
    ) -> AttemptRecord | None: ...
