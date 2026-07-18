create table if not exists places (
    id uuid primary key default gen_random_uuid(),
    provider text not null,
    provider_place_id text not null,
    name text not null,
    category text not null,
    tags text[] not null default '{}',
    address text not null,
    region_code text not null,
    lat double precision not null check (lat between -90 and 90),
    lng double precision not null check (lng between -180 and 180),
    opening_hours jsonb not null default '{}'::jsonb,
    price_level integer not null check (price_level >= 0),
    phone text,
    source_url text not null,
    unique (provider, provider_place_id)
);

insert into places (
    id, provider, provider_place_id, name, category, tags, address,
    region_code, lat, lng, opening_hours, price_level, phone, source_url
)
values
    (
        '30000000-0000-0000-0000-000000000001', 'mock', 'bucheon-001',
        '한국만화박물관', 'museum', array['indoor', 'solo_friendly'],
        '경기도 부천시 원미구 길주로 1', 'KR-41', 37.5088, 126.742,
        '{"summary": "10:00-18:00"}'::jsonb, 1, '032-310-3090',
        'https://www.komacon.kr/comicsmuseum'
    ),
    (
        '30000000-0000-0000-0000-000000000002', 'mock', 'bucheon-002',
        '상동호수공원', 'park', array['outdoor', 'walk', 'quiet'],
        '경기도 부천시 원미구 조마루로 15', 'KR-41', 37.5054, 126.7446,
        '{"summary": "24 hours"}'::jsonb, 0, null,
        'https://www.bucheon.go.kr'
    ),
    (
        '30000000-0000-0000-0000-000000000003', 'mock', 'bucheon-003',
        '부천아트센터', 'concert_hall', array['indoor', 'culture'],
        '경기도 부천시 원미구 소향로 165', 'KR-41', 37.5037, 126.7658,
        '{"summary": "Schedule dependent"}'::jsonb, 2, '1533-0202',
        'https://www.bac.or.kr'
    )
on conflict (id) do nothing;
