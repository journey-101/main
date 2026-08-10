from fastapi import HTTPException, status

from app.domains.places.repository import PlaceRepository
from app.domains.recommendations.repository import (
    PreferenceRecord,
    PreferenceRepository,
)
from app.domains.recommendations.schemas import (
    CreateRecommendationRequest,
    RecommendationData,
    UpdateUserPreferenceRequest,
    UserPreferenceData,
)
from app.domains.recommendations.scorer import score_places
from app.domains.recommendations.target_resolver import resolve_target
from app.domains.trips.repository import TripRepository


def get_user_preference(repo: PreferenceRepository, uid: str) -> UserPreferenceData:
    preference = repo.get(uid)
    if preference is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User preference not found"
        )
    return _to_data(preference)


def save_user_preference(
    repo: PreferenceRepository, uid: str, request: UpdateUserPreferenceRequest
) -> UserPreferenceData:
    record = PreferenceRecord(firebase_uid=uid, **request.model_dump())
    return _to_data(repo.save(record))


def create_recommendation(
    trips: TripRepository,
    preferences: PreferenceRepository,
    places: PlaceRepository,
    uid: str,
    request: CreateRecommendationRequest,
) -> RecommendationData:
    resolved = resolve_target(trips, places, uid, request.target)
    preference = preferences.get(uid)
    if preference is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User preference not found"
        )
    return RecommendationData(
        method=request.method,
        target=request.target.model_dump(mode="json"),
        fallback=resolved.fallback,
        items=score_places(_to_data(preference), resolved.candidates)[: request.limit],
    )


def _to_data(record: PreferenceRecord) -> UserPreferenceData:
    values = record.__dict__.copy()
    values.pop("firebase_uid")
    return UserPreferenceData(**values)
