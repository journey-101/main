"""Firebase UID projection and PostGIS schema."""

from alembic import op

revision = "20260810_02"
down_revision = "20260810_01"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    preserved_counts = {
        table: bind.exec_driver_sql(f"select count(*) from {table}").scalar_one()
        for table in (
            "app_users",
            "trips",
            "trip_attempts",
            "places",
            "user_preferences",
        )
    }
    users = bind.exec_driver_sql("select count(*) from app_users").scalar_one()
    mappings = bind.exec_driver_sql(
        "select count(*) from legacy_user_firebase_map"
    ).scalar_one()
    if users != mappings:
        raise RuntimeError(
            "Every legacy app_user must have exactly one Firebase UID mapping"
        )
    op.execute("create extension if not exists postgis")
    op.execute("""
        alter table trips drop constraint trips_user_id_fkey;
        alter table user_preferences drop constraint user_preferences_user_id_fkey;

        alter table app_users add column firebase_uid text;
        update app_users u set firebase_uid = m.firebase_uid from legacy_user_firebase_map m where m.legacy_user_uuid = u.id;
        alter table app_users alter column firebase_uid set not null;

        alter table trips add column firebase_uid text;
        update trips t set firebase_uid = m.firebase_uid from legacy_user_firebase_map m where m.legacy_user_uuid = t.user_id;
        alter table trips alter column firebase_uid set not null;

        alter table user_preferences add column firebase_uid text;
        update user_preferences p set firebase_uid = m.firebase_uid from legacy_user_firebase_map m where m.legacy_user_uuid = p.user_id;
        alter table user_preferences alter column firebase_uid set not null;
        alter table user_preferences add column preferred_categories_array text[];
        alter table user_preferences add column avoided_categories_array text[];
        update user_preferences set
          preferred_categories_array = array(select jsonb_array_elements_text(preferred_categories::jsonb)),
          avoided_categories_array = array(select jsonb_array_elements_text(avoided_categories::jsonb));
        alter table user_preferences alter column preferred_categories_array set not null;
        alter table user_preferences alter column avoided_categories_array set not null;

        drop table legacy_user_firebase_map;

        alter table app_users drop constraint app_users_pkey;
        alter table app_users drop column id;
        alter table app_users add primary key (firebase_uid);
        alter table app_users add column created_at timestamptz not null default now();
        alter table app_users add column updated_at timestamptz not null default now();

        alter table trips drop column user_id;
        alter table trips add constraint trips_firebase_uid_fkey foreign key (firebase_uid) references app_users(firebase_uid);
        alter table trips add column created_at timestamptz not null default now();
        alter table trips add column updated_at timestamptz not null default now();

        alter table user_preferences drop constraint user_preferences_pkey;
        alter table user_preferences drop column user_id;
        alter table user_preferences drop column preferred_categories;
        alter table user_preferences drop column avoided_categories;
        alter table user_preferences rename column preferred_categories_array to preferred_categories;
        alter table user_preferences rename column avoided_categories_array to avoided_categories;
        alter table user_preferences add primary key (firebase_uid);
        alter table user_preferences add constraint user_preferences_firebase_uid_fkey foreign key (firebase_uid) references app_users(firebase_uid);
        alter table user_preferences add column created_at timestamptz not null default now();

        alter table trip_attempts add constraint trip_attempts_status_check check (status in ('started', 'completed', 'aborted'));
        alter table trip_attempts add column updated_at timestamptz not null default now();
        create index ix_trip_attempts_latest on trip_attempts (trip_id, created_at desc, id desc);

        create table regions (
          id uuid primary key default gen_random_uuid(), code text not null unique, name text not null,
          boundary geometry(MultiPolygon, 4326), created_at timestamptz not null default now(), updated_at timestamptz not null default now()
        );
        insert into regions (code, name) select distinct region_code, region_code from places;
        alter table places add column region_id uuid;
        update places p set region_id = r.id from regions r where r.code = p.region_code;
        alter table places alter column region_id set not null;
        alter table places add constraint places_region_id_fkey foreign key (region_id) references regions(id);
        alter table places add column location geography(Point, 4326);
        update places set location = ST_SetSRID(ST_MakePoint(lng, lat), 4326)::geography;
        alter table places alter column location set not null;
        alter table places drop column region_code, drop column lat, drop column lng;
        alter table places add column created_at timestamptz not null default now();
        alter table places add column updated_at timestamptz not null default now();
        create index ix_regions_boundary_gist on regions using gist (boundary);
        create index ix_places_location_gist on places using gist (location);

        create table user_interest_regions (
          firebase_uid text not null references app_users(firebase_uid),
          region_id uuid not null references regions(id), created_at timestamptz not null default now(),
          primary key (firebase_uid, region_id)
        );
    """)
    _validate(bind, preserved_counts)


def _validate(bind: object, preserved_counts: dict[str, int]) -> None:
    checks = {
        "orphan trips": "select count(*) from trips t left join app_users u using(firebase_uid) where u.firebase_uid is null",
        "orphan preferences": "select count(*) from user_preferences p left join app_users u using(firebase_uid) where u.firebase_uid is null",
        "orphan attempts": "select count(*) from trip_attempts a left join trips t on t.id = a.trip_id where t.id is null",
        "orphan places": "select count(*) from places p left join regions r on r.id = p.region_id where r.id is null",
        "invalid locations": "select count(*) from places where not ST_IsValid(location::geometry)",
        "duplicate Firebase UIDs": "select count(*) - count(distinct firebase_uid) from app_users",
    }
    for label, sql in checks.items():
        if bind.exec_driver_sql(sql).scalar_one() != 0:
            raise RuntimeError(f"Migration validation failed: {label}")
    for table, expected in preserved_counts.items():
        actual = bind.exec_driver_sql(f"select count(*) from {table}").scalar_one()
        if actual != expected:
            raise RuntimeError(
                f"Migration validation failed: {table} count {actual} != {expected}"
            )


def downgrade() -> None:
    raise RuntimeError(
        "Firebase UID cutover is intentionally irreversible; restore the backup"
    )
