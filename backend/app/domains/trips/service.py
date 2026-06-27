from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.domains.trips import repository
from app.domains.trips.schemas import (
    CurrentTripAttemptData,
    TripAttemptData,
    TripAttemptMutationData,
    TripAttemptStatus,
    TripDetailData,
    TripListItemData,
)


def list_user_trips(session: Session, user_id: UUID) -> list[TripListItemData]:
    return [
        _map_trip_list_item(row)
        for row in repository.list_trips_by_user(session, user_id)
    ]


def create_trip(session: Session, user_id: UUID, title: str) -> TripListItemData:
    if repository.get_user(session, user_id) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    trip, attempt = repository.create_trip_with_attempt(session, user_id, title)
    return TripListItemData(
        id=trip["id"],
        user_id=trip["user_id"],
        title=trip["title"],
        current_attempt=_map_current_attempt(attempt),
    )


def get_trip_detail(session: Session, trip_id: UUID) -> TripDetailData:
    trip = repository.get_trip(session, trip_id)
    if trip is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Trip not found"
        )

    attempts = repository.get_trip_attempts(session, trip_id)
    return TripDetailData(
        id=trip["id"],
        user_id=trip["user_id"],
        title=trip["title"],
        attempts=[_map_attempt(attempt) for attempt in attempts],
    )


def update_trip(
    session: Session,
    trip_id: UUID,
    title: str,
) -> TripListItemData:
    trip = repository.get_trip(session, trip_id)
    if trip is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Trip not found"
        )

    updated_trip = repository.update_trip_title(session, trip_id, title)
    if updated_trip is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Trip not found"
        )

    current_attempt = repository.get_current_trip_attempt(session, trip_id)

    return TripListItemData(
        id=updated_trip["id"],
        user_id=updated_trip["user_id"],
        title=updated_trip["title"],
        current_attempt=(
            _map_current_attempt(current_attempt)
            if current_attempt is not None
            else None
        ),
    )


def create_trip_attempt(
    session: Session,
    trip_id: UUID,
    attempt_status: TripAttemptStatus,
) -> TripAttemptMutationData:
    trip = repository.get_trip(session, trip_id)
    if trip is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Trip not found"
        )

    return _map_attempt_mutation(
        repository.create_trip_attempt(session, trip_id, attempt_status)
    )


def update_trip_attempt(
    session: Session,
    trip_id: UUID,
    attempt_id: UUID,
    attempt_status: TripAttemptStatus | None,
    feedback_text: str | None,
) -> TripAttemptMutationData:
    trip = repository.get_trip(session, trip_id)
    if trip is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Trip not found"
        )

    attempt = repository.update_trip_attempt(
        session,
        trip_id,
        attempt_id,
        attempt_status,
        feedback_text,
    )
    if attempt is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trip attempt not found",
        )

    return _map_attempt_mutation(attempt)


def update_trip_attempt_feedback(
    session: Session,
    trip_id: UUID,
    attempt_id: UUID,
    feedback_text: str,
) -> TripAttemptMutationData:
    return update_trip_attempt(
        session,
        trip_id,
        attempt_id,
        attempt_status=None,
        feedback_text=feedback_text,
    )


def _map_trip_list_item(row: object) -> TripListItemData:
    return TripListItemData(
        id=row["id"],
        user_id=row["user_id"],
        title=row["title"],
        current_attempt=(
            CurrentTripAttemptData(
                id=row["current_attempt_id"],
                status=row["current_attempt_status"],
                feedback_text=row["current_attempt_feedback_text"],
            )
            if row["current_attempt_id"] is not None
            else None
        ),
    )


def _map_current_attempt(row: object) -> CurrentTripAttemptData:
    return CurrentTripAttemptData(
        id=row["id"],
        status=row["status"],
        feedback_text=row["feedback_text"],
    )


def _map_attempt(row: object) -> TripAttemptData:
    return TripAttemptData(
        id=row["id"],
        trip_id=row["trip_id"],
        status=row["status"],
        feedback_text=row["feedback_text"],
        created_at=row["created_at"],
    )


def _map_attempt_mutation(row: object) -> TripAttemptMutationData:
    return TripAttemptMutationData(
        id=row["id"],
        trip_id=row["trip_id"],
        status=row["status"],
        feedback_text=row["feedback_text"],
    )
