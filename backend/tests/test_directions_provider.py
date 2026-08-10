import pytest
from pydantic import ValidationError

from app.core.config import Settings, get_settings
from app.domains.directions.schemas import (
    DirectionPlaceData,
    GeoJsonLineString,
    TravelMode,
)
from app.integrations.directions.mock import MockDirectionsProvider
from app.integrations.directions.mock_odsay import MockOdsayClient
from app.integrations.directions.provider import get_directions_provider


def test_settings_default_to_mock_directions_provider() -> None:
    assert Settings(_env_file=None).directions_provider == "mock"


def test_settings_reject_unknown_directions_provider() -> None:
    with pytest.raises(ValidationError):
        Settings(_env_file=None, directions_provider="unknown")


def test_provider_factory_returns_mock_provider() -> None:
    get_settings.cache_clear()
    get_directions_provider.cache_clear()

    assert isinstance(get_directions_provider(), MockDirectionsProvider)


def test_mock_provider_returns_bent_polyline_in_longitude_latitude_order() -> None:
    origin = DirectionPlaceData(latitude=37.5034, longitude=126.766)
    destination = DirectionPlaceData(latitude=37.5088, longitude=126.742)

    route = MockDirectionsProvider().search(
        origin,
        destination,
        TravelMode.TRANSIT,
    )[0]

    assert route.geometry.coordinates == [
        (126.766, 37.5034),
        (126.7576, 37.50394),
        (126.7576, 37.50691),
        (126.748, 37.50691),
        (126.742, 37.5088),
    ]
    assert route.summary.distance_meters > 0
    assert route.summary.duration_seconds > 0


def test_geometry_requires_at_least_two_coordinates() -> None:
    with pytest.raises(ValidationError):
        GeoJsonLineString(coordinates=[(126.766, 37.5034)])


def test_mock_odsay_client_follows_search_then_load_lane_flow() -> None:
    client = MockOdsayClient()

    search_response = client.search_pub_trans_path_t(
        sx=126.766,
        sy=37.5034,
        ex=126.742,
        ey=37.5088,
    )
    path = search_response["result"]["path"][0]
    info = path["info"]

    assert path["pathType"] == 2
    assert info["totalDistance"] == 2490
    assert info["totalTime"] == 8
    assert info["mapObj"].startswith("12018:1:")

    lane_response = client.load_lane(map_object=f"0:0@{info['mapObj']}")
    graph_positions = lane_response["result"]["lane"][0]["section"][0][
        "graphPos"
    ]

    assert graph_positions[0] == {"x": 126.766, "y": 37.5034}
    assert graph_positions[-1] == {"x": 126.742, "y": 37.5088}
