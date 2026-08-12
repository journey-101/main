from uuid import UUID

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.domains.places.repository import PlaceRecord, PlaceSearch

PLACE_COLUMNS = """
    p.id, p.provider, p.provider_place_id, p.name, p.category, p.tags,
    p.address, r.code as region_code,
    ST_Y(p.location::geometry) as lat, ST_X(p.location::geometry) as lng,
    p.opening_hours, p.price_level, p.phone, p.source_url
"""


class PostgreSQLPlaceRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def search(self, query: PlaceSearch) -> list[PlaceRecord]:
        predicates: list[str] = []
        params: dict[str, object] = {"limit": query.limit}
        if query.keyword is not None:
            predicates.append(
                "(p.name ilike :keyword or p.address ilike :keyword or exists (select 1 from unnest(p.tags) tag where tag ilike :keyword))"
            )
            params["keyword"] = f"%{query.keyword}%"
        if query.region_code is not None:
            predicates.append("r.code = :region_code")
            params["region_code"] = query.region_code
        if query.category is not None:
            predicates.append("p.category = :category")
            params["category"] = query.category
        if query.lat is not None:
            predicates.append(
                "ST_DWithin(p.location, ST_SetSRID(ST_MakePoint(:lng, :lat), 4326)::geography, :radius_m)"
            )
            params.update(lat=query.lat, lng=query.lng, radius_m=query.radius_m)
        where = f"where {' and '.join(predicates)}" if predicates else ""
        rows = (
            self._session.execute(
                text(f"""
            select {PLACE_COLUMNS} from places p
            join regions r on r.id = p.region_id
            {where} order by p.id limit :limit
        """),
                params,
            )
            .mappings()
            .all()
        )
        return [self._map(row) for row in rows]

    def get(self, place_id: UUID) -> PlaceRecord | None:
        row = (
            self._session.execute(
                text(f"""
            select {PLACE_COLUMNS} from places p
            join regions r on r.id = p.region_id where p.id = :place_id
        """),
                {"place_id": place_id},
            )
            .mappings()
            .one_or_none()
        )
        return self._map(row) if row else None

    @staticmethod
    def _map(row: object) -> PlaceRecord:
        return PlaceRecord(
            id=row["id"],
            provider=row["provider"],
            provider_place_id=row["provider_place_id"],
            name=row["name"],
            category=row["category"],
            tags=list(row["tags"]),
            address=row["address"],
            region_code=row["region_code"],
            lat=float(row["lat"]),
            lng=float(row["lng"]),
            opening_hours=dict(row["opening_hours"]),
            price_level=row["price_level"],
            phone=row["phone"],
            source_url=row["source_url"],
        )
