from dataclasses import dataclass
from typing import cast
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.domains.places import repository as places_repository
from app.domains.recommendations import repository
from app.domains.recommendations.schemas import (
    PlaceRecommendationTarget,
    RecommendationFallbackData,
    RecommendationTarget,
    TripRecommendationTarget,
)
from app.domains.recommendations.scorer import CandidatePlace

PLACE_RECOMMENDATION_METADATA = {
    "30000000-0000-0000-0000-000000000001": {
        "quiet_score": 3,
        "walk_minutes": 10,
        "beginner_friendly": True,
    },
    "30000000-0000-0000-0000-000000000002": {
        "quiet_score": 5,
        "walk_minutes": 15,
        "beginner_friendly": True,
    },
    "30000000-0000-0000-0000-000000000003": {
        "quiet_score": 2,
        "walk_minutes": 25,
        "beginner_friendly": False,
    },
}
DEFAULT_METADATA = {"quiet_score": 3, "walk_minutes": 20, "beginner_friendly": True}


@dataclass(frozen=True)
class ResolvedRecommendationTarget:
    candidates: list[CandidatePlace]
    fallback: RecommendationFallbackData


def resolve_target(
    session: Session, user_id: UUID, target: RecommendationTarget
) -> ResolvedRecommendationTarget:
    if isinstance(target, PlaceRecommendationTarget):
        return ResolvedRecommendationTarget(
            candidates=_place_candidates(session, target.region_code),
            fallback=RecommendationFallbackData(used=False),
        )

    trip_target = cast(TripRecommendationTarget, target)
    trip = repository.get_trip(session, trip_target.trip_id)
    if trip is None or str(trip["user_id"]) != str(user_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trip not found")
    return ResolvedRecommendationTarget(
        candidates=_place_candidates(session, None),
        fallback=RecommendationFallbackData(
            used=True,
            reason="trip_place_not_available",
            fallback_target={"type": "place"},
        ),
    )


def _place_candidates(session: Session, region_code: str | None) -> list[CandidatePlace]:
    places = places_repository.list_places(session)
    if region_code is not None:
        places = [place for place in places if place["region_code"] == region_code]
    candidates: list[CandidatePlace] = []
    for place in places:
        metadata = DEFAULT_METADATA | PLACE_RECOMMENDATION_METADATA.get(
            str(place["id"]), {}
        )
        candidates.append(
            CandidatePlace(
                id=place["id"],
                name=place["name"],
                category=place["category"],
                quiet_score=metadata["quiet_score"],
                walk_minutes=metadata["walk_minutes"],
                beginner_friendly=metadata["beginner_friendly"],
            )
        )
    return candidates
