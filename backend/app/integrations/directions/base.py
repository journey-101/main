from typing import Protocol

from app.domains.directions.schemas import (
    DirectionPlaceData,
    DirectionRouteData,
    TravelMode,
)


class DirectionsProvider(Protocol):
    def search(
        self,
        origin: DirectionPlaceData,
        destination: DirectionPlaceData,
        mode: TravelMode,
    ) -> list[DirectionRouteData]: ...
