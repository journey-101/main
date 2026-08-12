from sqlalchemy import text
from sqlalchemy.orm import Session

from app.domains.recommendations.repository import PreferenceRecord


class PostgreSQLPreferenceRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def get(self, firebase_uid: str) -> PreferenceRecord | None:
        row = (
            self._session.execute(
                text("""
            select firebase_uid, preferred_categories, avoided_categories,
                   prefers_quiet, max_walk_minutes, is_first_time_traveler
            from user_preferences where firebase_uid = :uid
        """),
                {"uid": firebase_uid},
            )
            .mappings()
            .one_or_none()
        )
        return self._map(row) if row else None

    def save(self, preference: PreferenceRecord) -> PreferenceRecord:
        self._session.execute(
            text("""
            insert into user_preferences (
                firebase_uid, preferred_categories, avoided_categories, prefers_quiet,
                max_walk_minutes, is_first_time_traveler
            ) values (:firebase_uid, :preferred_categories, :avoided_categories,
                      :prefers_quiet, :max_walk_minutes, :is_first_time_traveler)
            on conflict (firebase_uid) do update set
                preferred_categories = excluded.preferred_categories,
                avoided_categories = excluded.avoided_categories,
                prefers_quiet = excluded.prefers_quiet,
                max_walk_minutes = excluded.max_walk_minutes,
                is_first_time_traveler = excluded.is_first_time_traveler,
                updated_at = now()
        """),
            preference.__dict__,
        )
        saved = self.get(preference.firebase_uid)
        if saved is None:
            raise RuntimeError("Saved preference could not be loaded")
        return saved

    @staticmethod
    def _map(row: object) -> PreferenceRecord:
        return PreferenceRecord(
            firebase_uid=row["firebase_uid"],
            preferred_categories=list(row["preferred_categories"]),
            avoided_categories=list(row["avoided_categories"]),
            prefers_quiet=row["prefers_quiet"],
            max_walk_minutes=row["max_walk_minutes"],
            is_first_time_traveler=row["is_first_time_traveler"],
        )
