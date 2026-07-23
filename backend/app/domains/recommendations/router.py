from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db_session
from app.domains.health.schemas import SuccessResponse
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
from app.domains.recommendations.service import (
    create_recommendation,
    get_user_preference,
    save_user_preference,
)

router = APIRouter()


@router.get("/me/preferences", response_model=SuccessResponse[UserPreferenceData])
def get_preferences(
    user_id: UUID, session: Session = Depends(get_db_session)
) -> SuccessResponse[UserPreferenceData]:
    return SuccessResponse(data=get_user_preference(session, user_id))


@router.put("/me/preferences", response_model=SuccessResponse[UserPreferenceData])
def put_preferences(
    request: UpdateUserPreferenceRequest,
    session: Session = Depends(get_db_session),
) -> SuccessResponse[UserPreferenceData]:
    return SuccessResponse(data=save_user_preference(session, request))


@router.post("/recommendations", response_model=SuccessResponse[RecommendationData])
def post_recommendation(
    request: CreateRecommendationRequest,
    session: Session = Depends(get_db_session),
) -> SuccessResponse[RecommendationData]:
    return SuccessResponse(data=create_recommendation(session, request))


@router.post("/recommendations/places", response_model=SuccessResponse[RecommendationData])
def post_place_recommendation(
    request: CreatePlaceRecommendationRequest,
    session: Session = Depends(get_db_session),
) -> SuccessResponse[RecommendationData]:
    normalized = CreateRecommendationRequest(
        user_id=request.user_id,
        method=RecommendationMethod.preference_mock,
        target=PlaceRecommendationTarget(type="place", region_code=request.region_code),
        limit=request.limit,
    )
    return SuccessResponse(data=create_recommendation(session, normalized))


@router.post("/recommendations/trips", response_model=SuccessResponse[RecommendationData])
def post_trip_recommendation(
    request: CreateTripRecommendationRequest,
    session: Session = Depends(get_db_session),
) -> SuccessResponse[RecommendationData]:
    normalized = CreateRecommendationRequest(
        user_id=request.user_id,
        method=RecommendationMethod.preference_mock,
        target=TripRecommendationTarget(type="trip", trip_id=request.trip_id),
        limit=request.limit,
    )
    return SuccessResponse(data=create_recommendation(session, normalized))
