from dataclasses import dataclass
from typing import Protocol
from uuid import UUID


@dataclass(frozen=True)
class RegionRecord:
    id: UUID
    code: str
    name: str


class InterestRegionRepository(Protocol):
    def list_for_user(self, firebase_uid: str) -> list[RegionRecord]: ...
    def replace_for_user(self, firebase_uid: str, region_ids: list[UUID]) -> None: ...
