"""Legacy UUID schema baseline."""

from alembic import op

revision = "20260810_01"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("create extension if not exists pgcrypto")
    op.execute("""
        create table app_users (id uuid primary key default gen_random_uuid());
        create table trips (
            id uuid primary key default gen_random_uuid(), user_id uuid not null references app_users(id), title text not null
        );
        create table trip_attempts (
            id uuid primary key default gen_random_uuid(), trip_id uuid not null references trips(id),
            status text not null, feedback_text text, created_at timestamptz not null default now()
        );
        create table places (
            id uuid primary key default gen_random_uuid(), provider text not null,
            provider_place_id text not null, name text not null, category text not null,
            tags text[] not null default '{}', address text not null, region_code text not null,
            lat double precision not null check (lat between -90 and 90),
            lng double precision not null check (lng between -180 and 180),
            opening_hours jsonb not null default '{}'::jsonb, price_level integer not null check (price_level >= 0),
            phone text, source_url text not null, unique(provider, provider_place_id)
        );
        create table user_preferences (
            user_id uuid primary key references app_users(id), preferred_categories text not null,
            avoided_categories text not null, prefers_quiet boolean not null,
            max_walk_minutes integer not null, is_first_time_traveler boolean not null,
            updated_at timestamptz not null default now()
        );
        create table legacy_user_firebase_map (
            legacy_user_uuid uuid primary key references app_users(id), firebase_uid text not null unique
        );
    """)


def downgrade() -> None:
    op.execute(
        "drop table legacy_user_firebase_map, user_preferences, places, trip_attempts, trips, app_users"
    )
