create table if not exists user_preferences (
    user_id uuid primary key references app_users(id),
    preferred_categories text not null,
    avoided_categories text not null,
    prefers_quiet boolean not null,
    max_walk_minutes integer not null,
    is_first_time_traveler boolean not null,
    updated_at timestamptz not null default now()
);

insert into user_preferences (
    user_id,
    preferred_categories,
    avoided_categories,
    prefers_quiet,
    max_walk_minutes,
    is_first_time_traveler
)
values (
    '00000000-0000-0000-0000-000000000000',
    '["museum", "park"]',
    '["concert_hall"]',
    true,
    20,
    true
)
on conflict (user_id) do nothing;
