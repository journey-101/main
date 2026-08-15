from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends

from app.core.auth import CurrentUser, get_current_user
from app.db.uow import UnitOfWork, get_uow
from app.domains.health.schemas import SuccessResponse
from app.domains.trips.schemas import (
    CreateTripAttemptRequest,
    CreateTripRequest,
    TripAttemptMutationData,
    TripDetailData,
    TripListItemData,
    UpdateTripAttemptFeedbackRequest,
    UpdateTripAttemptRequest,
    UpdateTripRequest,
)
from app.domains.trips import service

router = APIRouter()
User = Annotated[CurrentUser, Depends(get_current_user)]
Uow = Annotated[UnitOfWork, Depends(get_uow)]


@router.get("", response_model=SuccessResponse[list[TripListItemData]])
def get_trips(user: User, uow: Uow) -> SuccessResponse[list[TripListItemData]]:
    return SuccessResponse(data=service.list_user_trips(uow.trips, user.uid))


@router.post("", response_model=SuccessResponse[TripListItemData], status_code=201)
def post_trip(
    request: CreateTripRequest, user: User, uow: Uow
) -> SuccessResponse[TripListItemData]:
    return SuccessResponse(data=service.create_trip(uow.trips, user.uid, request.title))


@router.get("/{trip_id}", response_model=SuccessResponse[TripDetailData])
def get_trip(trip_id: UUID, user: User, uow: Uow) -> SuccessResponse[TripDetailData]:
    return SuccessResponse(data=service.get_trip_detail(uow.trips, user.uid, trip_id))


@router.patch("/{trip_id}", response_model=SuccessResponse[TripListItemData])
def patch_trip(
    trip_id: UUID, request: UpdateTripRequest, user: User, uow: Uow
) -> SuccessResponse[TripListItemData]:
    return SuccessResponse(
        data=service.update_trip(uow.trips, user.uid, trip_id, request.title)
    )


@router.post(
    "/{trip_id}/attempts",
    response_model=SuccessResponse[TripAttemptMutationData],
    status_code=201,
)
def post_trip_attempt(
    trip_id: UUID, request: CreateTripAttemptRequest, user: User, uow: Uow
) -> SuccessResponse[TripAttemptMutationData]:
    return SuccessResponse(
        data=service.create_trip_attempt(uow.trips, user.uid, trip_id, request.status)
    )


@router.patch(
    "/{trip_id}/attempts/{attempt_id}/feedback",
    response_model=SuccessResponse[TripAttemptMutationData],
)
def patch_trip_attempt_feedback(
    trip_id: UUID,
    attempt_id: UUID,
    request: UpdateTripAttemptFeedbackRequest,
    user: User,
    uow: Uow,
) -> SuccessResponse[TripAttemptMutationData]:
    return SuccessResponse(
        data=service.update_trip_attempt(
            uow.trips, user.uid, trip_id, attempt_id, None, request.feedback_text
        )
    )


@router.patch(
    "/{trip_id}/attempts/{attempt_id}",
    response_model=SuccessResponse[TripAttemptMutationData],
)
def patch_trip_attempt(
    trip_id: UUID,
    attempt_id: UUID,
    request: UpdateTripAttemptRequest,
    user: User,
    uow: Uow,
) -> SuccessResponse[TripAttemptMutationData]:
    return SuccessResponse(
        data=service.update_trip_attempt(
            uow.trips,
            user.uid,
            trip_id,
            attempt_id,
            request.status,
            request.feedback_text,
        )
    )
