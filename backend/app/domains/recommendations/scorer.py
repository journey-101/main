from dataclasses import dataclass
from uuid import UUID

from app.domains.recommendations.schemas import RecommendationItemData, UserPreferenceData


@dataclass(frozen=True)
class CandidatePlace:
    id: UUID
    name: str
    category: str
    quiet_score: int = 3
    walk_minutes: int = 20
    beginner_friendly: bool = True


def score_places(
    preference: UserPreferenceData, candidates: list[CandidatePlace]
) -> list[RecommendationItemData]:
    scored = [_score_place(preference, candidate) for candidate in candidates]
    scored.sort(key=lambda item: (-item.score, item.place_name, str(item.place_id)))
    return [item.model_copy(update={"rank": rank}) for rank, item in enumerate(scored, 1)]


def _score_place(
    preference: UserPreferenceData, place: CandidatePlace
) -> RecommendationItemData:
    score = 0
    reasons: list[str] = []
    if place.category in preference.preferred_categories:
        score += 50
        reasons.append("preferred_category")
    if place.category in preference.avoided_categories:
        score -= 100
        reasons.append("avoided_category")
    if preference.prefers_quiet:
        if place.quiet_score >= 4:
            score += 20
            reasons.append("quiet_place")
        elif place.quiet_score <= 2:
            score -= 10
            reasons.append("noisy_place")
    if place.walk_minutes <= preference.max_walk_minutes:
        score += 20
        reasons.append("within_walk_limit")
    else:
        score -= 30
        reasons.append("over_walk_limit")
    if preference.is_first_time_traveler:
        if place.beginner_friendly:
            score += 15
            reasons.append("beginner_friendly")
        else:
            score -= 15
            reasons.append("not_beginner_friendly")
    return RecommendationItemData(
        place_id=place.id,
        place_name=place.name,
        category=place.category,
        score=score,
        rank=0,
        reasons=reasons,
    )
