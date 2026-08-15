from dataclasses import dataclass
from typing import Protocol
from uuid import UUID


@dataclass(frozen=True)
class PlaceRecord:
    id: UUID
    provider: str
    provider_place_id: str
    name: str
    category: str
    tags: list[str]
    address: str
    region_code: str
    lat: float
    lng: float
    opening_hours: dict[str, str]
    price_level: int
    phone: str | None
    source_url: str


@dataclass(frozen=True)
class PlaceSearch:
    keyword: str | None = None
    region_code: str | None = None
    category: str | None = None
    lat: float | None = None
    lng: float | None = None
    radius_m: int | None = None
    limit: int = 20


class PlaceRepository(Protocol):
    def search(self, query: PlaceSearch) -> list[PlaceRecord]: ...
    def get(self, place_id: UUID) -> PlaceRecord | None: ...
