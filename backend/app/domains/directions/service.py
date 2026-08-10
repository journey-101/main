from fastapi import HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.domains.directions.schemas import (
    DirectionPlaceData,
    DirectionSearchData,
    DirectionSearchRequest,
)
from app.domains.places import repository as places_repository
from app.integrations.directions.base import DirectionsProvider


def search_directions(
    session: Session,
    request: DirectionSearchRequest,
    provider: DirectionsProvider,
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
    return DirectionSearchData(
        routes=provider.search(origin, destination, request.mode)
    )
