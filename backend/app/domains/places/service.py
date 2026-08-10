from uuid import UUID

from fastapi import HTTPException, status

from app.domains.places.repository import PlaceRecord, PlaceRepository, PlaceSearch
from app.domains.places.schemas import (
    PlaceDetailData,
    PlaceListItemData,
    PlaceSearchData,
    PlaceSearchQuery,
)


def search_places(repo: PlaceRepository, query: PlaceSearchQuery) -> PlaceSearchData:
    records = repo.search(
        PlaceSearch(
            keyword=query.q,
            region_code=query.region_code,
            category=query.category,
            lat=query.lat,
            lng=query.lng,
            radius_m=query.radius_m,
            limit=query.limit,
        )
    )
    return PlaceSearchData(
        items=[_to_list_item(row) for row in records], next_cursor=None
    )


def get_place_detail(repo: PlaceRepository, place_id: UUID) -> PlaceDetailData:
    row = repo.get(place_id)
    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Place not found"
        )
    return _to_detail(row)


def _to_detail(row: PlaceRecord) -> PlaceDetailData:
    return PlaceDetailData(**row.__dict__)


def _to_list_item(row: PlaceRecord) -> PlaceListItemData:
    return PlaceListItemData.model_validate(row.__dict__)
