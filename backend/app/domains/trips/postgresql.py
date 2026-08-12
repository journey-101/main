from uuid import UUID, uuid4

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.domains.trips.repository import AttemptRecord, TripListRecord, TripRecord
from app.domains.trips.schemas import TripAttemptStatus


class PostgreSQLTripRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def list_for_user(self, firebase_uid: str) -> list[TripListRecord]:
        rows = (
            self._session.execute(
                text("""
            select t.id, t.firebase_uid, t.title,
                   a.id attempt_id, t.id attempt_trip_id, a.status attempt_status,
                   a.feedback_text attempt_feedback_text, a.created_at attempt_created_at
            from trips t
            left join lateral (
                select id, status, feedback_text, created_at
                from trip_attempts where trip_id = t.id
                order by created_at desc, id desc limit 1
            ) a on true
            where t.firebase_uid = :uid order by t.title, t.id
        """),
                {"uid": firebase_uid},
            )
            .mappings()
            .all()
        )
        return [
            TripListRecord(
                self._trip(row),
                self._attempt(row, "attempt_") if row["attempt_id"] else None,
            )
            for row in rows
        ]

    def get(self, trip_id: UUID, firebase_uid: str) -> TripRecord | None:
        row = (
            self._session.execute(
                text("""
            select id, firebase_uid, title from trips
            where id = :trip_id and firebase_uid = :uid
        """),
                {"trip_id": trip_id, "uid": firebase_uid},
            )
            .mappings()
            .one_or_none()
        )
        return self._trip(row) if row else None

    def attempts(self, trip_id: UUID, firebase_uid: str) -> list[AttemptRecord]:
        rows = (
            self._session.execute(
                text("""
            select a.id, a.trip_id, a.status, a.feedback_text, a.created_at
            from trip_attempts a join trips t on t.id = a.trip_id
            where a.trip_id = :trip_id and t.firebase_uid = :uid
            order by a.created_at desc, a.id desc
        """),
                {"trip_id": trip_id, "uid": firebase_uid},
            )
            .mappings()
            .all()
        )
        return [self._attempt(row) for row in rows]

    def current_attempt(self, trip_id: UUID, firebase_uid: str) -> AttemptRecord | None:
        row = (
            self._session.execute(
                text("""
            select a.id, a.trip_id, a.status, a.feedback_text, a.created_at
            from trip_attempts a join trips t on t.id = a.trip_id
            where a.trip_id = :trip_id and t.firebase_uid = :uid
            order by a.created_at desc, a.id desc limit 1
        """),
                {"trip_id": trip_id, "uid": firebase_uid},
            )
            .mappings()
            .one_or_none()
        )
        return self._attempt(row) if row else None

    def create_with_attempt(
        self, firebase_uid: str, title: str
    ) -> tuple[TripRecord, AttemptRecord]:
        trip_id, attempt_id = uuid4(), uuid4()
        trip_row = (
            self._session.execute(
                text("""
            insert into trips (id, firebase_uid, title) values (:id, :uid, :title)
            returning id, firebase_uid, title
        """),
                {"id": trip_id, "uid": firebase_uid, "title": title},
            )
            .mappings()
            .one()
        )
        attempt_row = (
            self._session.execute(
                text("""
            insert into trip_attempts (id, trip_id, status)
            values (:id, :trip_id, 'started')
            returning id, trip_id, status, feedback_text, created_at
        """),
                {"id": attempt_id, "trip_id": trip_id},
            )
            .mappings()
            .one()
        )
        return self._trip(trip_row), self._attempt(attempt_row)

    def update_title(
        self, trip_id: UUID, firebase_uid: str, title: str
    ) -> TripRecord | None:
        row = (
            self._session.execute(
                text("""
            update trips set title = :title, updated_at = now()
            where id = :trip_id and firebase_uid = :uid
            returning id, firebase_uid, title
        """),
                {"trip_id": trip_id, "uid": firebase_uid, "title": title},
            )
            .mappings()
            .one_or_none()
        )
        return self._trip(row) if row else None

    def create_attempt(
        self, trip_id: UUID, firebase_uid: str, status: TripAttemptStatus
    ) -> AttemptRecord | None:
        row = (
            self._session.execute(
                text("""
            insert into trip_attempts (id, trip_id, status)
            select :id, t.id, :status from trips t
            where t.id = :trip_id and t.firebase_uid = :uid
            returning id, trip_id, status, feedback_text, created_at
        """),
                {
                    "id": uuid4(),
                    "trip_id": trip_id,
                    "uid": firebase_uid,
                    "status": status.value,
                },
            )
            .mappings()
            .one_or_none()
        )
        return self._attempt(row) if row else None

    def update_attempt(
        self,
        trip_id: UUID,
        attempt_id: UUID,
        firebase_uid: str,
        status: TripAttemptStatus | None,
        feedback_text: str | None,
    ) -> AttemptRecord | None:
        assignments = ["updated_at = now()"]
        params: dict[str, object] = {
            "trip_id": trip_id,
            "attempt_id": attempt_id,
            "uid": firebase_uid,
        }
        if status is not None:
            assignments.append("status = :status")
            params["status"] = status.value
        if feedback_text is not None:
            assignments.append("feedback_text = :feedback_text")
            params["feedback_text"] = feedback_text
        row = (
            self._session.execute(
                text(f"""
            update trip_attempts a set {", ".join(assignments)}
            from trips t where a.id = :attempt_id and a.trip_id = :trip_id
              and t.id = a.trip_id and t.firebase_uid = :uid
            returning a.id, a.trip_id, a.status, a.feedback_text, a.created_at
        """),
                params,
            )
            .mappings()
            .one_or_none()
        )
        return self._attempt(row) if row else None

    @staticmethod
    def _trip(row: object) -> TripRecord:
        return TripRecord(
            id=row["id"], firebase_uid=row["firebase_uid"], title=row["title"]
        )

    @staticmethod
    def _attempt(row: object, prefix: str = "") -> AttemptRecord:
        return AttemptRecord(
            id=row[f"{prefix}id"],
            trip_id=row[f"{prefix}trip_id"],
            status=TripAttemptStatus(row[f"{prefix}status"]),
            feedback_text=row[f"{prefix}feedback_text"],
            created_at=row[f"{prefix}created_at"],
        )
