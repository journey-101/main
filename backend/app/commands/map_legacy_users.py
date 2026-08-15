import argparse
import csv
from pathlib import Path
from uuid import UUID

from sqlalchemy import create_engine, text

from app.core.config import get_settings

REQUIRED_TABLES = {"app_users", "trips", "trip_attempts", "places", "user_preferences"}
REQUIRED_COLUMNS = {
    "app_users": {"id"},
    "trips": {"id", "user_id", "title"},
    "trip_attempts": {"id", "trip_id", "status", "feedback_text", "created_at"},
    "places": {"id", "region_code", "lat", "lng"},
    "user_preferences": {"user_id", "preferred_categories", "avoided_categories"},
}


def load_mapping(path: Path) -> list[tuple[UUID, str]]:
    with path.open(encoding="utf-8", newline="") as stream:
        reader = csv.DictReader(stream)
        if reader.fieldnames != ["legacy_user_uuid", "firebase_uid"]:
            raise ValueError("CSV header must be legacy_user_uuid,firebase_uid")
        rows = [
            (UUID(row["legacy_user_uuid"]), row["firebase_uid"].strip())
            for row in reader
        ]
    if any(not uid for _, uid in rows):
        raise ValueError("Firebase UID cannot be empty")
    if len({legacy for legacy, _ in rows}) != len(rows):
        raise ValueError("Duplicate legacy UUID in mapping")
    if len({uid for _, uid in rows}) != len(rows):
        raise ValueError("Duplicate Firebase UID in mapping")
    return rows


def apply_mapping(path: Path) -> None:
    rows = load_mapping(path)
    engine = create_engine(get_settings().resolved_database_url)
    with engine.begin() as connection:
        existing_tables = set(
            connection.execute(
                text("""
            select table_name from information_schema.tables where table_schema = 'public'
        """)
            ).scalars()
        )
        if not REQUIRED_TABLES <= existing_tables:
            raise RuntimeError(
                f"Legacy schema mismatch; missing: {sorted(REQUIRED_TABLES - existing_tables)}"
            )
        columns = connection.execute(
            text("""
                select table_name, column_name from information_schema.columns
                where table_schema = 'public' and table_name = any(:tables)
            """),
            {"tables": list(REQUIRED_TABLES)},
        ).all()
        actual_columns: dict[str, set[str]] = {
            table: set() for table in REQUIRED_TABLES
        }
        for table, column in columns:
            actual_columns[table].add(column)
        mismatches = {
            table: sorted(required - actual_columns[table])
            for table, required in REQUIRED_COLUMNS.items()
            if not required <= actual_columns[table]
        }
        if mismatches:
            raise RuntimeError(f"Legacy schema column mismatch: {mismatches}")
        legacy_users = set(
            connection.execute(text("select id from app_users")).scalars()
        )
        mapped_users = {legacy for legacy, _ in rows}
        if legacy_users != mapped_users:
            missing = sorted(str(value) for value in legacy_users - mapped_users)
            unknown = sorted(str(value) for value in mapped_users - legacy_users)
            raise RuntimeError(
                f"Mapping must cover users exactly; missing={missing}, unknown={unknown}"
            )
        connection.execute(
            text("""
            create table if not exists legacy_user_firebase_map (
              legacy_user_uuid uuid primary key references app_users(id), firebase_uid text not null unique
            )
        """)
        )
        connection.execute(text("delete from legacy_user_firebase_map"))
        for legacy, uid in rows:
            connection.execute(
                text("""
                insert into legacy_user_firebase_map (legacy_user_uuid, firebase_uid) values (:legacy, :uid)
            """),
                {"legacy": legacy, "uid": uid},
            )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Validate and stage UUID-to-Firebase-UID mapping"
    )
    parser.add_argument("csv", type=Path)
    args = parser.parse_args()
    apply_mapping(args.csv)


if __name__ == "__main__":
    main()
