import json
from json import JSONDecodeError
from math import asin, cos, radians, sin, sqrt
from pathlib import Path
from uuid import UUID

from fastapi import HTTPException, status
from pydantic import TypeAdapter, ValidationError

from app.domains.places.schemas import (
    PlaceDetailData,
    PlaceListItemData,
    PlaceSearchData,
    PlaceSearchQuery,
)

DATA_FILE = Path(__file__).parent / "data" / "places.json"
PLACE_LIST_ADAPTER = TypeAdapter(list[PlaceDetailData])


def search_places(query: PlaceSearchQuery) -> PlaceSearchData:
    places = _load_places()

    if query.q is not None:
        keyword = query.q.casefold()
        places = [
            place
            for place in places
            if keyword in place.name.casefold()
            or keyword in place.address.casefold()
            or any(keyword in tag.casefold() for tag in place.tags)
        ]
    if query.region_code is not None:
        places = [
            place for place in places if place.region_code == query.region_code
        ]
    if query.category is not None:
        places = [place for place in places if place.category == query.category]
    if query.lat is not None and query.lng is not None and query.radius_m is not None:
        places = [
            place
            for place in places
            if _distance_m(query.lat, query.lng, place.lat, place.lng)
            <= query.radius_m
        ]

    return PlaceSearchData(
        items=[_to_list_item(place) for place in places[: query.limit]],
        next_cursor=None,
    )


def get_place_detail(place_id: UUID) -> PlaceDetailData:
    for place in _load_places():
        if place.id == place_id:
            return place

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Place not found",
    )


def _load_places() -> list[PlaceDetailData]:
    try:
        raw_places = json.loads(DATA_FILE.read_text(encoding="utf-8"))
        return PLACE_LIST_ADAPTER.validate_python(raw_places)
    except (OSError, JSONDecodeError, ValidationError, TypeError) as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unknown place data error",
        ) from exc


def _to_list_item(place: PlaceDetailData) -> PlaceListItemData:
    return PlaceListItemData.model_validate(place.model_dump())


def _distance_m(
    origin_lat: float,
    origin_lng: float,
    destination_lat: float,
    destination_lng: float,
) -> float:
    earth_radius_m = 6_371_000
    lat_delta = radians(destination_lat - origin_lat)
    lng_delta = radians(destination_lng - origin_lng)
    origin_lat_radians = radians(origin_lat)
    destination_lat_radians = radians(destination_lat)

    haversine = (
        sin(lat_delta / 2) ** 2
        + cos(origin_lat_radians)
        * cos(destination_lat_radians)
        * sin(lng_delta / 2) ** 2
    )
    return 2 * earth_radius_m * asin(sqrt(haversine))
