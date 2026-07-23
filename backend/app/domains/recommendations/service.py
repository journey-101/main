from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID

from app.domains.recommendations import repository
from app.domains.recommendations.schemas import (
    CreateRecommendationRequest,
    RecommendationData,
    UpdateUserPreferenceRequest,
    UserPreferenceData,
)
from app.domains.recommendations.scorer import score_places
from app.domains.recommendations.target_resolver import resolve_target


def get_user_preference(session: Session, user_id: UUID) -> UserPreferenceData:
    preference = repository.get_user_preference(session, user_id)
    if preference is None:
        if repository.get_user(session, user_id) is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User preference not found"
        )
    return preference


def save_user_preference(
    session: Session, request: UpdateUserPreferenceRequest
) -> UserPreferenceData:
    if repository.get_user(session, request.user_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return repository.save_user_preference(
        session, UserPreferenceData.model_validate(request)
    )


def create_recommendation(
    session: Session, request: CreateRecommendationRequest
) -> RecommendationData:
    if repository.get_user(session, request.user_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    resolved = resolve_target(session, request.user_id, request.target)
    preference = repository.get_user_preference(session, request.user_id)
    if preference is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User preference not found"
        )
    return RecommendationData(
        method=request.method,
        target=request.target.model_dump(mode="json"),
        fallback=resolved.fallback,
        items=score_places(preference, resolved.candidates)[: request.limit],
    )
