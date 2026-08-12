from sqlalchemy import create_engine, text

from app.core.config import get_settings

SEED_UID = "local-dev-user"


def seed() -> None:
    engine = create_engine(get_settings().resolved_database_url)
    with engine.begin() as connection:
        connection.execute(
            text(
                "insert into app_users(firebase_uid) values (:uid) on conflict do nothing"
            ),
            {"uid": SEED_UID},
        )
        connection.execute(
            text("""
          insert into regions(id, code, name, boundary) values (
            '40000000-0000-0000-0000-000000000001', 'KR-41', '경기도',
            ST_Multi(ST_GeomFromText('POLYGON((126 37,127 37,127 38,126 38,126 37))',4326)))
          on conflict(code) do nothing
        """)
        )
        connection.execute(
            text("""
          insert into user_preferences(firebase_uid, preferred_categories, avoided_categories, prefers_quiet, max_walk_minutes, is_first_time_traveler)
          values (:uid, array['museum','park'], array['concert_hall'], true, 20, true) on conflict(firebase_uid) do nothing
        """),
            {"uid": SEED_UID},
        )
        connection.execute(
            text("""
          insert into trips(id, firebase_uid, title) values ('10000000-0000-0000-0000-000000000001', :uid, '북촌 산책') on conflict(id) do nothing
        """),
            {"uid": SEED_UID},
        )
        connection.execute(
            text("""
          insert into trip_attempts(id, trip_id, status) values ('20000000-0000-0000-0000-000000000001', '10000000-0000-0000-0000-000000000001', 'started') on conflict(id) do nothing
        """)
        )
        places = [
            (
                "30000000-0000-0000-0000-000000000001",
                "bucheon-001",
                "한국만화박물관",
                "museum",
                37.5088,
                126.742,
            ),
            (
                "30000000-0000-0000-0000-000000000002",
                "bucheon-002",
                "상동호수공원",
                "park",
                37.5054,
                126.7446,
            ),
            (
                "30000000-0000-0000-0000-000000000003",
                "bucheon-003",
                "부천아트센터",
                "concert_hall",
                37.5037,
                126.7658,
            ),
        ]
        for place_id, provider_id, name, category, lat, lng in places:
            connection.execute(
                text("""
              insert into places(id, provider, provider_place_id, name, category, tags, address, region_id, location, opening_hours, price_level, source_url)
              values (:id, 'mock', :provider_id, :name, :category, '{}', '경기도 부천시',
                '40000000-0000-0000-0000-000000000001', ST_SetSRID(ST_MakePoint(:lng,:lat),4326)::geography, '{}', 0, 'https://example.com')
              on conflict(id) do nothing
            """),
                {
                    "id": place_id,
                    "provider_id": provider_id,
                    "name": name,
                    "category": category,
                    "lat": lat,
                    "lng": lng,
                },
            )


if __name__ == "__main__":
    seed()
