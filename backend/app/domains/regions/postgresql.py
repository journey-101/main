from uuid import UUID

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.domains.regions.repository import RegionRecord


class PostgreSQLInterestRegionRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def list_for_user(self, firebase_uid: str) -> list[RegionRecord]:
        rows = (
            self._session.execute(
                text("""
            select r.id, r.code, r.name from regions r
            join user_interest_regions uir on uir.region_id = r.id
            where uir.firebase_uid = :uid order by r.code
        """),
                {"uid": firebase_uid},
            )
            .mappings()
            .all()
        )
        return [RegionRecord(**row) for row in rows]

    def replace_for_user(self, firebase_uid: str, region_ids: list[UUID]) -> None:
        self._session.execute(
            text("delete from user_interest_regions where firebase_uid = :uid"),
            {"uid": firebase_uid},
        )
        for region_id in dict.fromkeys(region_ids):
            self._session.execute(
                text("""
                insert into user_interest_regions (firebase_uid, region_id)
                values (:uid, :region_id)
            """),
                {"uid": firebase_uid, "region_id": region_id},
            )
