from enum import Enum
from typing import Annotated, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class RecommendationMethod(str, Enum):
    preference_mock = "preference_mock"


class UserPreferenceData(BaseModel):
    preferred_categories: list[str]
    avoided_categories: list[str]
    prefers_quiet: bool
    max_walk_minutes: int
    is_first_time_traveler: bool


class UpdateUserPreferenceRequest(UserPreferenceData):
    model_config = ConfigDict(extra="forbid")

    max_walk_minutes: int = Field(ge=1)


class PlaceRecommendationTarget(BaseModel):
    type: Literal["place"]
    region_code: str | None = None


class TripRecommendationTarget(BaseModel):
    type: Literal["trip"]
    trip_id: UUID


RecommendationTarget = Annotated[
    PlaceRecommendationTarget | TripRecommendationTarget,
    Field(discriminator="type"),
]


class CreateRecommendationRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    method: RecommendationMethod = RecommendationMethod.preference_mock
    target: RecommendationTarget
    limit: int = Field(default=10, ge=1, le=100)


class CreatePlaceRecommendationRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    region_code: str | None = None
    limit: int = Field(default=10, ge=1, le=100)


class CreateTripRecommendationRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    trip_id: UUID
    limit: int = Field(default=10, ge=1, le=100)


class RecommendationFallbackData(BaseModel):
    used: bool
    reason: str | None = None
    fallback_target: dict[str, str] | None = None


class RecommendationItemData(BaseModel):
    place_id: UUID
    place_name: str
    category: str
    score: int
    rank: int
    reasons: list[str]


class RecommendationData(BaseModel):
    method: RecommendationMethod
    target: dict[str, str]
    fallback: RecommendationFallbackData
    items: list[RecommendationItemData]
