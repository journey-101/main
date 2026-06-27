from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, ConfigDict, model_validator


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


class TripAttemptMutationData(BaseModel):
    id: UUID
    trip_id: UUID
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


class CreateTripAttemptRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: TripAttemptStatus = TripAttemptStatus.started


class UpdateTripAttemptRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: TripAttemptStatus | None = None
    feedback_text: str | None = None

    @model_validator(mode="after")
    def require_update_field(self) -> "UpdateTripAttemptRequest":
        if self.status is None and self.feedback_text is None:
            raise ValueError("At least one of status or feedback_text is required")
        return self


class UpdateTripAttemptFeedbackRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    feedback_text: str
