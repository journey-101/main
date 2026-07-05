from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator


class PlaceSearchQuery(BaseModel):
    model_config = ConfigDict(extra="forbid")

    q: str | None = Field(default=None, min_length=1)
    region_code: str | None = None
    category: str | None = None
    lat: float | None = Field(default=None, ge=-90, le=90)
    lng: float | None = Field(default=None, ge=-180, le=180)
    radius_m: int | None = Field(default=None, gt=0)
    limit: int = Field(default=20, ge=1, le=100)
    cursor: str | None = None

    @model_validator(mode="after")
    def require_complete_location(self) -> "PlaceSearchQuery":
        location_values = (self.lat, self.lng, self.radius_m)
        if any(value is not None for value in location_values) and not all(
            value is not None for value in location_values
        ):
            raise ValueError("lat, lng, and radius_m must be provided together")
        return self


class PlaceListItemData(BaseModel):
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
    price_level: int
    source_url: str


class PlaceSearchData(BaseModel):
    items: list[PlaceListItemData]
    next_cursor: str | None


class PlaceDetailData(PlaceListItemData):
    opening_hours: dict[str, str]
    phone: str | None
