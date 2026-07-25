from math import asin, cos, radians, sin, sqrt

from fastapi import HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.domains.directions.schemas import (
    DirectionPlaceData,
    DirectionRouteData,
    DirectionSearchData,
    DirectionSearchRequest,
    DirectionSummaryData,
    GeoJsonLineString,
    TravelMode,
)
from app.domains.places import repository as places_repository

AVERAGE_SPEED_MPS = {
    TravelMode.WALKING: 1.2,
    TravelMode.DRIVING: 8.3,
    TravelMode.TRANSIT: 5.5,
}


def search_directions(
    session: Session,
    request: DirectionSearchRequest,
) -> DirectionSearchData:
    try:
        place = places_repository.get_place(session, request.place_id)
    except SQLAlchemyError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unknown place data error",
        ) from exc

    if place is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Place not found",
        )

    distance_meters = round(
        _distance_m(
            request.origin.latitude,
            request.origin.longitude,
            place["lat"],
            place["lng"],
        )
    )
    duration_seconds = round(distance_meters / AVERAGE_SPEED_MPS[request.mode])

    origin = DirectionPlaceData(
        latitude=request.origin.latitude,
        longitude=request.origin.longitude,
    )
    destination = DirectionPlaceData(
        place_id=request.place_id,
        name=place["name"],
        latitude=place["lat"],
        longitude=place["lng"],
    )
    route = DirectionRouteData(
        provider="mock",
        mode=request.mode,
        origin=origin,
        destination=destination,
        summary=DirectionSummaryData(
            distance_meters=distance_meters,
            duration_seconds=duration_seconds,
        ),
        geometry=GeoJsonLineString(
            coordinates=[
                (origin.longitude, origin.latitude),
                (destination.longitude, destination.latitude),
            ]
        ),
    )
    return DirectionSearchData(routes=[route])


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
