from functools import lru_cache

from app.core.config import get_settings
from app.integrations.directions.base import DirectionsProvider
from app.integrations.directions.mock import MockDirectionsProvider


@lru_cache
def get_directions_provider() -> DirectionsProvider:
    settings = get_settings()
    if settings.directions_provider == "mock":
        return MockDirectionsProvider()

    raise RuntimeError(
        f"Directions provider is not implemented: {settings.directions_provider}"
    )
