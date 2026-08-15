import argparse
import json
from pathlib import Path

from sqlalchemy import create_engine, text

from app.core.config import get_settings


def import_regions(path: Path) -> None:
    document = json.loads(path.read_text(encoding="utf-8"))
    if document.get("type") != "FeatureCollection" or not document.get("features"):
        raise ValueError("GeoJSON must be a non-empty FeatureCollection")
    prepared: list[dict[str, str]] = []
    codes: set[str] = set()
    for feature in document["features"]:
        properties = feature.get("properties") or {}
        code, name, geometry = (
            properties.get("code"),
            properties.get("name"),
            feature.get("geometry"),
        )
        if not code or not name or not geometry:
            raise ValueError(
                "Every feature requires properties.code, properties.name, and geometry"
            )
        if code in codes:
            raise ValueError(f"Duplicate region code: {code}")
        codes.add(code)
        prepared.append({"code": code, "name": name, "geometry": json.dumps(geometry)})

    engine = create_engine(get_settings().resolved_database_url)
    with engine.begin() as connection:
        for region in prepared:
            valid = connection.execute(
                text("""
                select GeometryType(g) in ('POLYGON', 'MULTIPOLYGON') and ST_IsValid(g)
                from (select ST_SetSRID(ST_GeomFromGeoJSON(:geometry), 4326) g) value
            """),
                region,
            ).scalar_one()
            if not valid:
                raise ValueError(f"Invalid polygon geometry for {region['code']}")
        for region in prepared:
            connection.execute(
                text("""
                insert into regions (code, name, boundary)
                values (:code, :name, ST_Multi(ST_SetSRID(ST_GeomFromGeoJSON(:geometry), 4326)))
                on conflict (code) do update set name = excluded.name,
                  boundary = excluded.boundary, updated_at = now()
            """),
                region,
            )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Atomically import managed region boundaries"
    )
    parser.add_argument("geojson", type=Path)
    args = parser.parse_args()
    import_regions(args.geojson)


if __name__ == "__main__":
    main()
