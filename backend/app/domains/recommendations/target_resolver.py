from dataclasses import dataclass
from typing import cast

from fastapi import HTTPException, status

from app.domains.places.repository import PlaceRepository, PlaceSearch
from app.domains.recommendations.schemas import (
    PlaceRecommendationTarget,
    RecommendationFallbackData,
    RecommendationTarget,
    TripRecommendationTarget,
)
from app.domains.recommendations.scorer import CandidatePlace
from app.domains.trips.repository import TripRepository

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
    trips: TripRepository,
    places: PlaceRepository,
    uid: str,
    target: RecommendationTarget,
) -> ResolvedRecommendationTarget:
    if isinstance(target, PlaceRecommendationTarget):
        return ResolvedRecommendationTarget(
            _place_candidates(places, target.region_code),
            RecommendationFallbackData(used=False),
        )
    trip_target = cast(TripRecommendationTarget, target)
    if trips.get(trip_target.trip_id, uid) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Trip not found"
        )
    return ResolvedRecommendationTarget(
        _place_candidates(places, None),
        RecommendationFallbackData(
            used=True,
            reason="trip_place_not_available",
            fallback_target={"type": "place"},
        ),
    )


def _place_candidates(
    repo: PlaceRepository, region_code: str | None
) -> list[CandidatePlace]:
    candidates = []
    for place in repo.search(PlaceSearch(region_code=region_code, limit=100)):
        metadata = DEFAULT_METADATA | PLACE_RECOMMENDATION_METADATA.get(
            str(place.id), {}
        )
        candidates.append(
            CandidatePlace(
                id=place.id, name=place.name, category=place.category, **metadata
            )
        )
    return candidates
