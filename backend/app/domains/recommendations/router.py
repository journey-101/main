from typing import Annotated

from fastapi import APIRouter, Depends

from app.core.auth import CurrentUser, get_current_user
from app.db.uow import UnitOfWork, get_uow
from app.domains.health.schemas import SuccessResponse
from app.domains.recommendations import service
from app.domains.recommendations.schemas import (
    CreatePlaceRecommendationRequest,
    CreateRecommendationRequest,
    CreateTripRecommendationRequest,
    PlaceRecommendationTarget,
    RecommendationData,
    RecommendationMethod,
    TripRecommendationTarget,
    UpdateUserPreferenceRequest,
    UserPreferenceData,
)

router = APIRouter()
User = Annotated[CurrentUser, Depends(get_current_user)]
Uow = Annotated[UnitOfWork, Depends(get_uow)]


@router.get("/me/preferences", response_model=SuccessResponse[UserPreferenceData])
def get_preferences(user: User, uow: Uow) -> SuccessResponse[UserPreferenceData]:
    return SuccessResponse(data=service.get_user_preference(uow.preferences, user.uid))


@router.put("/me/preferences", response_model=SuccessResponse[UserPreferenceData])
def put_preferences(
    request: UpdateUserPreferenceRequest, user: User, uow: Uow
) -> SuccessResponse[UserPreferenceData]:
    return SuccessResponse(
        data=service.save_user_preference(uow.preferences, user.uid, request)
    )


@router.post("/recommendations", response_model=SuccessResponse[RecommendationData])
def post_recommendation(
    request: CreateRecommendationRequest, user: User, uow: Uow
) -> SuccessResponse[RecommendationData]:
    return SuccessResponse(
        data=service.create_recommendation(
            uow.trips, uow.preferences, uow.places, user.uid, request
        )
    )


@router.post(
    "/recommendations/places", response_model=SuccessResponse[RecommendationData]
)
def post_place_recommendation(
    request: CreatePlaceRecommendationRequest, user: User, uow: Uow
) -> SuccessResponse[RecommendationData]:
    normalized = CreateRecommendationRequest(
        method=RecommendationMethod.preference_mock,
        target=PlaceRecommendationTarget(type="place", region_code=request.region_code),
        limit=request.limit,
    )
    return post_recommendation(normalized, user, uow)


@router.post(
    "/recommendations/trips", response_model=SuccessResponse[RecommendationData]
)
def post_trip_recommendation(
    request: CreateTripRecommendationRequest, user: User, uow: Uow
) -> SuccessResponse[RecommendationData]:
    normalized = CreateRecommendationRequest(
        method=RecommendationMethod.preference_mock,
        target=TripRecommendationTarget(type="trip", trip_id=request.trip_id),
        limit=request.limit,
    )
    return post_recommendation(normalized, user, uow)
