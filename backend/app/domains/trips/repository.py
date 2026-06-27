from collections.abc import Sequence
from uuid import UUID, uuid4

from sqlalchemy import RowMapping, text
from sqlalchemy.orm import Session

from app.domains.trips.schemas import TripAttemptStatus


def list_trips_by_user(session: Session, user_id: UUID) -> Sequence[RowMapping]:
    result = session.execute(
        text(
            """
            with current_attempts as (
                select
                    id,
                    trip_id,
                    status,
                    feedback_text,
                    created_at,
                    row_number() over (
                        partition by trip_id
                        order by created_at desc, id desc
                    ) as attempt_rank
                from trip_attempts
            )
            select
                t.id,
                t.user_id,
                t.title,
                ca.id as current_attempt_id,
                ca.status as current_attempt_status,
                ca.feedback_text as current_attempt_feedback_text
            from trips t
            left join current_attempts ca
                on ca.trip_id = t.id
                and ca.attempt_rank = 1
            where t.user_id = :user_id
            order by t.title, t.id
            """
        ),
        {"user_id": str(user_id)},
    )
    return result.mappings().all()


def get_user(session: Session, user_id: UUID) -> RowMapping | None:
    result = session.execute(
        text("select id from app_users where id = :user_id"),
        {"user_id": str(user_id)},
    )
    return result.mappings().one_or_none()


def get_trip(session: Session, trip_id: UUID) -> RowMapping | None:
    result = session.execute(
        text("select id, user_id, title from trips where id = :trip_id"),
        {"trip_id": str(trip_id)},
    )
    return result.mappings().one_or_none()


def get_trip_attempts(session: Session, trip_id: UUID) -> Sequence[RowMapping]:
    result = session.execute(
        text(
            """
            select id, trip_id, status, feedback_text, created_at
            from trip_attempts
            where trip_id = :trip_id
            order by created_at desc, id desc
            """
        ),
        {"trip_id": str(trip_id)},
    )
    return result.mappings().all()


def get_current_trip_attempt(session: Session, trip_id: UUID) -> RowMapping | None:
    result = session.execute(
        text(
            """
            select id, trip_id, status, feedback_text, created_at
            from trip_attempts
            where trip_id = :trip_id
            order by created_at desc, id desc
            limit 1
            """
        ),
        {"trip_id": str(trip_id)},
    )
    return result.mappings().one_or_none()


def get_trip_attempt(
    session: Session, trip_id: UUID, attempt_id: UUID
) -> RowMapping | None:
    result = session.execute(
        text(
            """
            select id, trip_id, status, feedback_text, created_at
            from trip_attempts
            where trip_id = :trip_id
                and id = :attempt_id
            """
        ),
        {"trip_id": str(trip_id), "attempt_id": str(attempt_id)},
    )
    return result.mappings().one_or_none()


def create_trip_with_attempt(
    session: Session,
    user_id: UUID,
    title: str,
) -> tuple[RowMapping, RowMapping]:
    trip_id = uuid4()
    attempt_id = uuid4()

    session.execute(
        text(
            """
            insert into trips (id, user_id, title)
            values (:trip_id, :user_id, :title)
            """
        ),
        {"trip_id": str(trip_id), "user_id": str(user_id), "title": title},
    )
    session.execute(
        text(
            """
            insert into trip_attempts (id, trip_id, status, feedback_text)
            values (:attempt_id, :trip_id, :status, :feedback_text)
            """
        ),
        {
            "attempt_id": str(attempt_id),
            "trip_id": str(trip_id),
            "status": TripAttemptStatus.started.value,
            "feedback_text": None,
        },
    )
    trip = get_trip(session, trip_id)
    attempt = get_current_trip_attempt(session, trip_id)
    if trip is None or attempt is None:
        raise RuntimeError("Created trip could not be loaded")

    return trip, attempt


def update_trip_title(session: Session, trip_id: UUID, title: str) -> RowMapping | None:
    session.execute(
        text(
            """
            update trips
            set title = :title
            where id = :trip_id
            """
        ),
        {"trip_id": str(trip_id), "title": title},
    )
    return get_trip(session, trip_id)


def create_trip_attempt(
    session: Session,
    trip_id: UUID,
    status: TripAttemptStatus,
) -> RowMapping:
    attempt_id = uuid4()
    session.execute(
        text(
            """
            insert into trip_attempts (id, trip_id, status, feedback_text)
            values (:attempt_id, :trip_id, :status, :feedback_text)
            """
        ),
        {
            "attempt_id": str(attempt_id),
            "trip_id": str(trip_id),
            "status": status.value,
            "feedback_text": None,
        },
    )
    attempt = get_trip_attempt(session, trip_id, attempt_id)
    if attempt is None:
        raise RuntimeError("Created trip attempt could not be loaded")
    return attempt


def update_trip_attempt(
    session: Session,
    trip_id: UUID,
    attempt_id: UUID,
    status: TripAttemptStatus | None,
    feedback_text: str | None,
) -> RowMapping | None:
    assignments: list[str] = []
    params: dict[str, str | None] = {
        "trip_id": str(trip_id),
        "attempt_id": str(attempt_id),
    }
    if status is not None:
        assignments.append("status = :status")
        params["status"] = status.value
    if feedback_text is not None:
        assignments.append("feedback_text = :feedback_text")
        params["feedback_text"] = feedback_text

    if not assignments:
        return get_trip_attempt(session, trip_id, attempt_id)

    result = session.execute(
        text(
            f"""
            update trip_attempts
            set {", ".join(assignments)}
            where id = :attempt_id
                and trip_id = :trip_id
            """
        ),
        params,
    )
    if result.rowcount == 0:
        return None
    return get_trip_attempt(session, trip_id, attempt_id)
