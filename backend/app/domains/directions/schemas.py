from enum import Enum
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class TravelMode(str, Enum):
    WALKING = "walking"
    DRIVING = "driving"
    TRANSIT = "transit"


class Coordinate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)


class DirectionSearchRequest(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "example": {
                "place_id": "30000000-0000-0000-0000-000000000001",
                "origin": {
                    "latitude": 37.5034,
                    "longitude": 126.766,
                },
                "mode": "walking",
            }
        },
    )

    place_id: UUID
    origin: Coordinate
    mode: TravelMode


class DirectionPlaceData(Coordinate):
    place_id: UUID | None = None
    name: str | None = None


class GeoJsonLineString(BaseModel):
    type: str = "LineString"
    coordinates: list[tuple[float, float]]


class DirectionSummaryData(BaseModel):
    distance_meters: int
    duration_seconds: int


class DirectionRouteData(BaseModel):
    provider: str
    mode: TravelMode
    origin: DirectionPlaceData
    destination: DirectionPlaceData
    summary: DirectionSummaryData
    geometry: GeoJsonLineString


class DirectionSearchData(BaseModel):
    routes: list[DirectionRouteData]
