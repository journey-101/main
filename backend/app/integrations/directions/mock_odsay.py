from math import asin, ceil, cos, radians, sin, sqrt
from threading import Lock

from app.domains.directions.schemas import DirectionPlaceData
from app.integrations.directions.odsay import OdsayResponse


class MockOdsayClient:
    """In-memory double that follows ODsay's two-request response shapes."""

    def __init__(self) -> None:
        self._lanes: dict[str, list[tuple[float, float]]] = {}
        self._lock = Lock()
        self._next_route_id = 12018

    def search_pub_trans_path_t(
        self,
        *,
        sx: float,
        sy: float,
        ex: float,
        ey: float,
    ) -> OdsayResponse:
        coordinates = _mock_polyline_coordinates(
            DirectionPlaceData(latitude=sy, longitude=sx),
            DirectionPlaceData(latitude=ey, longitude=ex),
        )
        distance_meters = round(_polyline_distance_m(coordinates))
        total_time_minutes = ceil(distance_meters / 5.5 / 60)

        with self._lock:
            route_id = self._next_route_id
            self._next_route_id += 1
            map_obj = f"{route_id}:1:0:{len(coordinates) - 1}"
            map_object = f"0:0@{map_obj}"
            self._lanes[map_object] = coordinates

        return {
            "result": {
                "searchType": 0,
                "busCount": 1,
                "subwayCount": 0,
                "subwayBusCount": 0,
                "pointDistance": distance_meters,
                "path": [
                    {
                        "pathType": 2,
                        "info": {
                            "trafficDistance": distance_meters,
                            "totalWalk": 0,
                            "totalTime": total_time_minutes,
                            "payment": 0,
                            "busTransitCount": 0,
                            "subwayTransitCount": 0,
                            "mapObj": map_obj,
                            "totalDistance": distance_meters,
                        },
                        "subPath": [],
                    }
                ],
            }
        }

    def load_lane(self, *, map_object: str) -> OdsayResponse:
        with self._lock:
            coordinates = self._lanes[map_object]

        return {
            "result": {
                "lane": [
                    {
                        "class": 1,
                        "type": 11,
                        "section": [
                            {
                                "graphPos": [
                                    {"x": longitude, "y": latitude}
                                    for longitude, latitude in coordinates
                                ]
                            }
                        ],
                    }
                ],
                "boundary": {
                    "left": min(point[0] for point in coordinates),
                    "top": max(point[1] for point in coordinates),
                    "right": max(point[0] for point in coordinates),
                    "bottom": min(point[1] for point in coordinates),
                },
            }
        }


def _mock_polyline_coordinates(
    origin: DirectionPlaceData,
    destination: DirectionPlaceData,
) -> list[tuple[float, float]]:
    longitude_delta = destination.longitude - origin.longitude
    latitude_delta = destination.latitude - origin.latitude

    def point(longitude_ratio: float, latitude_ratio: float) -> tuple[float, float]:
        return (
            round(origin.longitude + longitude_delta * longitude_ratio, 6),
            round(origin.latitude + latitude_delta * latitude_ratio, 6),
        )

    return [
        (origin.longitude, origin.latitude),
        point(0.35, 0.10),
        point(0.35, 0.65),
        point(0.75, 0.65),
        (destination.longitude, destination.latitude),
    ]


def _polyline_distance_m(coordinates: list[tuple[float, float]]) -> float:
    return sum(
        _distance_m(
            origin_latitude,
            origin_longitude,
            destination_latitude,
            destination_longitude,
        )
        for (
            (origin_longitude, origin_latitude),
            (destination_longitude, destination_latitude),
        ) in zip(coordinates, coordinates[1:], strict=False)
    )


def _distance_m(
    origin_latitude: float,
    origin_longitude: float,
    destination_latitude: float,
    destination_longitude: float,
) -> float:
    earth_radius_m = 6_371_000
    latitude_delta = radians(destination_latitude - origin_latitude)
    longitude_delta = radians(destination_longitude - origin_longitude)
    origin_latitude_radians = radians(origin_latitude)
    destination_latitude_radians = radians(destination_latitude)
    haversine = (
        sin(latitude_delta / 2) ** 2
        + cos(origin_latitude_radians)
        * cos(destination_latitude_radians)
        * sin(longitude_delta / 2) ** 2
    )
    return 2 * earth_radius_m * asin(sqrt(haversine))
