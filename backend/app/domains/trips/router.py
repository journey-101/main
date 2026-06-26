from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db_session
from app.domains.health.schemas import SuccessResponse
from app.domains.trips.schemas import (
    CreateTripRequest,
    TripDetailData,
    TripListItemData,
    UpdateTripRequest,
)
from app.domains.trips.service import (
    create_trip,
    get_trip_detail,
    list_user_trips,
    update_trip,
)

router = APIRouter()


@router.get("", response_model=SuccessResponse[list[TripListItemData]])
def get_trips(
    user_id: UUID,
    session: Session = Depends(get_db_session),
) -> SuccessResponse[list[TripListItemData]]:
    return SuccessResponse(data=list_user_trips(session, user_id))


@router.post("", response_model=SuccessResponse[TripListItemData], status_code=201)
def post_trip(
    request: CreateTripRequest,
    session: Session = Depends(get_db_session),
) -> SuccessResponse[TripListItemData]:
    return SuccessResponse(data=create_trip(session, request.user_id, request.title))


@router.get("/{trip_id}", response_model=SuccessResponse[TripDetailData])
def get_trip(
    trip_id: UUID,
    session: Session = Depends(get_db_session),
) -> SuccessResponse[TripDetailData]:
    return SuccessResponse(data=get_trip_detail(session, trip_id))


@router.patch("/{trip_id}", response_model=SuccessResponse[TripListItemData])
def patch_trip(
    trip_id: UUID,
    request: UpdateTripRequest,
    session: Session = Depends(get_db_session),
) -> SuccessResponse[TripListItemData]:
