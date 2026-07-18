from collections.abc import Sequence
from uuid import UUID

from sqlalchemy import RowMapping, text
from sqlalchemy.orm import Session


PLACE_COLUMNS = """
    id, provider, provider_place_id, name, category, tags, address,
    region_code, lat, lng, opening_hours, price_level, phone, source_url
"""


def list_places(session: Session) -> Sequence[RowMapping]:
    result = session.execute(text(f"select {PLACE_COLUMNS} from places order by id"))
    return result.mappings().all()


def get_place(session: Session, place_id: UUID) -> RowMapping | None:
    result = session.execute(
        text(f"select {PLACE_COLUMNS} from places where id = :place_id"),
        {"place_id": str(place_id)},
    )
    return result.mappings().one_or_none()
