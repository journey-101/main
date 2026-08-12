from uuid import UUID

from fastapi import HTTPException, status

from app.domains.trips.repository import AttemptRecord, TripListRecord, TripRepository
from app.domains.trips.schemas import (
    CurrentTripAttemptData,
    TripAttemptData,
    TripAttemptMutationData,
    TripAttemptStatus,
    TripDetailData,
    TripListItemData,
)


def list_user_trips(repo: TripRepository, uid: str) -> list[TripListItemData]:
    return [_map_list_item(row) for row in repo.list_for_user(uid)]


def create_trip(repo: TripRepository, uid: str, title: str) -> TripListItemData:
    trip, attempt = repo.create_with_attempt(uid, title)
    return TripListItemData(
        id=trip.id, title=trip.title, current_attempt=_map_current(attempt)
    )


def get_trip_detail(repo: TripRepository, uid: str, trip_id: UUID) -> TripDetailData:
    trip = repo.get(trip_id, uid)
    if trip is None:
        raise _not_found("Trip not found")
    return TripDetailData(
        id=trip.id,
        title=trip.title,
        attempts=[_map_attempt(a) for a in repo.attempts(trip_id, uid)],
    )


def update_trip(
    repo: TripRepository, uid: str, trip_id: UUID, title: str
) -> TripListItemData:
    trip = repo.update_title(trip_id, uid, title)
    if trip is None:
        raise _not_found("Trip not found")
    current = repo.current_attempt(trip_id, uid)
    return TripListItemData(
        id=trip.id,
        title=trip.title,
        current_attempt=_map_current(current) if current else None,
    )


def create_trip_attempt(
    repo: TripRepository, uid: str, trip_id: UUID, attempt_status: TripAttemptStatus
) -> TripAttemptMutationData:
    attempt = repo.create_attempt(trip_id, uid, attempt_status)
    if attempt is None:
        raise _not_found("Trip not found")
    return _map_mutation(attempt)


def update_trip_attempt(
    repo: TripRepository,
    uid: str,
    trip_id: UUID,
    attempt_id: UUID,
    attempt_status: TripAttemptStatus | None,
    feedback_text: str | None,
) -> TripAttemptMutationData:
    if repo.get(trip_id, uid) is None:
        raise _not_found("Trip not found")
    attempt = repo.update_attempt(
        trip_id, attempt_id, uid, attempt_status, feedback_text
    )
    if attempt is None:
        raise _not_found("Trip attempt not found")
    return _map_mutation(attempt)


def _map_list_item(row: TripListRecord) -> TripListItemData:
    return TripListItemData(
        id=row.trip.id,
        title=row.trip.title,
        current_attempt=_map_current(row.current_attempt)
        if row.current_attempt
        else None,
    )


def _map_current(row: AttemptRecord) -> CurrentTripAttemptData:
    return CurrentTripAttemptData(
        id=row.id, status=row.status, feedback_text=row.feedback_text
    )


def _map_attempt(row: AttemptRecord) -> TripAttemptData:
    return TripAttemptData(
        id=row.id,
        trip_id=row.trip_id,
        status=row.status,
        feedback_text=row.feedback_text,
        created_at=row.created_at,
    )


def _map_mutation(row: AttemptRecord) -> TripAttemptMutationData:
    return TripAttemptMutationData(
        id=row.id,
        trip_id=row.trip_id,
        status=row.status,
        feedback_text=row.feedback_text,
    )


def _not_found(detail: str) -> HTTPException:
    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail)
