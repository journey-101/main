create extension if not exists pgcrypto;

create table if not exists app_users (
    id uuid primary key default gen_random_uuid()
);

create table if not exists trips (
    id uuid primary key default gen_random_uuid(),
    user_id uuid not null references app_users(id),
    title text not null
);

create table if not exists trip_attempts (
    id uuid primary key default gen_random_uuid(),
    trip_id uuid not null references trips(id),
    status text not null,
    feedback_text text,
    created_at timestamptz not null default now()
);

insert into app_users (id)
values ('00000000-0000-0000-0000-000000000000')
on conflict (id) do nothing;

insert into trips (id, user_id, title)
values (
    '10000000-0000-0000-0000-000000000001',
    '00000000-0000-0000-0000-000000000000',
    '북촌 산책'
)
on conflict (id) do nothing;

insert into trip_attempts (id, trip_id, status, feedback_text)
values (
    '20000000-0000-0000-0000-000000000001',
    '10000000-0000-0000-0000-000000000001',
    'started',
    null
)
on conflict (id) do nothing;
