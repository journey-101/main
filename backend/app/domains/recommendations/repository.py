import json
from uuid import UUID

from sqlalchemy import RowMapping, text
from sqlalchemy.orm import Session

from app.domains.recommendations.schemas import UserPreferenceData


def get_user(session: Session, user_id: UUID) -> RowMapping | None:
    return session.execute(
        text("select id from app_users where id = :user_id"),
        {"user_id": str(user_id)},
    ).mappings().one_or_none()


def get_trip(session: Session, trip_id: UUID) -> RowMapping | None:
    return session.execute(
        text("select id, user_id from trips where id = :trip_id"),
        {"trip_id": str(trip_id)},
    ).mappings().one_or_none()


def get_user_preference(session: Session, user_id: UUID) -> UserPreferenceData | None:
    row = session.execute(
        text(
            """
            select user_id, preferred_categories, avoided_categories, prefers_quiet,
                   max_walk_minutes, is_first_time_traveler
            from user_preferences where user_id = :user_id
            """
        ),
        {"user_id": str(user_id)},
    ).mappings().one_or_none()
    if row is None:
        return None
    return UserPreferenceData(
        user_id=row["user_id"],
        preferred_categories=json.loads(row["preferred_categories"]),
        avoided_categories=json.loads(row["avoided_categories"]),
        prefers_quiet=bool(row["prefers_quiet"]),
        max_walk_minutes=row["max_walk_minutes"],
        is_first_time_traveler=bool(row["is_first_time_traveler"]),
    )


def save_user_preference(
    session: Session, preference: UserPreferenceData
) -> UserPreferenceData:
    params = preference.model_dump(mode="json")
    params["preferred_categories"] = json.dumps(params["preferred_categories"])
    params["avoided_categories"] = json.dumps(params["avoided_categories"])
    session.execute(
        text(
            """
            insert into user_preferences (
                user_id, preferred_categories, avoided_categories, prefers_quiet,
                max_walk_minutes, is_first_time_traveler
            ) values (
                :user_id, :preferred_categories, :avoided_categories, :prefers_quiet,
                :max_walk_minutes, :is_first_time_traveler
            )
            on conflict (user_id) do update set
                preferred_categories = excluded.preferred_categories,
                avoided_categories = excluded.avoided_categories,
                prefers_quiet = excluded.prefers_quiet,
                max_walk_minutes = excluded.max_walk_minutes,
                is_first_time_traveler = excluded.is_first_time_traveler,
                updated_at = current_timestamp
            """
        ),
        params,
    )
    saved = get_user_preference(session, preference.user_id)
    if saved is None:
        raise RuntimeError("Saved user preference could not be loaded")
    return saved
