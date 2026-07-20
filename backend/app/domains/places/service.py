import json
from math import asin, cos, radians, sin, sqrt
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.domains.places import repository
from app.domains.places.schemas import (
    PlaceDetailData,
    PlaceListItemData,
    PlaceSearchData,
    PlaceSearchQuery,
)

def search_places(session: Session, query: PlaceSearchQuery) -> PlaceSearchData:
    try:
        places = [_map_place(row) for row in repository.list_places(session)]
    except (SQLAlchemyError, TypeError, ValueError, json.JSONDecodeError) as exc:
        raise _unknown_data_error() from exc

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


def get_place_detail(session: Session, place_id: UUID) -> PlaceDetailData:
    try:
        row = repository.get_place(session, place_id)
        if row is not None:
            return _map_place(row)
    except (SQLAlchemyError, TypeError, ValueError, json.JSONDecodeError) as exc:
        raise _unknown_data_error() from exc

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Place not found")


def _map_place(row: object) -> PlaceDetailData:
    tags = row["tags"]
    opening_hours = row["opening_hours"]
    if isinstance(tags, str):
        tags = json.loads(tags)
    if isinstance(opening_hours, str):
        opening_hours = json.loads(opening_hours)
    return PlaceDetailData(
        id=row["id"], provider=row["provider"],
        provider_place_id=row["provider_place_id"], name=row["name"],
        category=row["category"], tags=tags, address=row["address"],
        region_code=row["region_code"], lat=row["lat"], lng=row["lng"],
        opening_hours=opening_hours, price_level=row["price_level"],
        phone=row["phone"], source_url=row["source_url"],
    )


def _unknown_data_error() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Unknown place data error",
    )


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
