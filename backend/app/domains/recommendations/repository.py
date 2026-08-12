from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class PreferenceRecord:
    firebase_uid: str
    preferred_categories: list[str]
    avoided_categories: list[str]
    prefers_quiet: bool
    max_walk_minutes: int
    is_first_time_traveler: bool


class PreferenceRepository(Protocol):
    def get(self, firebase_uid: str) -> PreferenceRecord | None: ...
    def save(self, preference: PreferenceRecord) -> PreferenceRecord: ...
