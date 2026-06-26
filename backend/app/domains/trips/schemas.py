from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class TripAttemptStatus(str, Enum):
    started = "started"
    completed = "completed"
    aborted = "aborted"


class TripAttemptData(BaseModel):
    id: UUID
    trip_id: UUID
    status: TripAttemptStatus
    feedback_text: str | None
    created_at: datetime


class CurrentTripAttemptData(BaseModel):
    id: UUID
    status: TripAttemptStatus
    feedback_text: str | None


class TripListItemData(BaseModel):
    id: UUID
    user_id: UUID
    title: str
    current_attempt: CurrentTripAttemptData | None


class TripDetailData(BaseModel):
    id: UUID
    user_id: UUID
    title: str
    attempts: list[TripAttemptData]


class CreateTripRequest(BaseModel):
    user_id: UUID
    title: str


class UpdateTripRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str
