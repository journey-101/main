from app.domains.directions.schemas import (
    DirectionPlaceData,
    DirectionRouteData,
    DirectionSummaryData,
    GeoJsonLineString,
    TravelMode,
)
from app.integrations.directions.mock_odsay import MockOdsayClient
from app.integrations.directions.odsay import OdsayClient, OdsayResponse


class MockDirectionsProvider:
    def __init__(self, client: OdsayClient | None = None) -> None:
        self.client = client or MockOdsayClient()

    def search(
        self,
        origin: DirectionPlaceData,
        destination: DirectionPlaceData,
        mode: TravelMode,
    ) -> list[DirectionRouteData]:
        search_response = self.client.search_pub_trans_path_t(
            sx=origin.longitude,
            sy=origin.latitude,
            ex=destination.longitude,
            ey=destination.latitude,
        )

        return [
            self._to_route(
                path,
                origin=origin,
                destination=destination,
                mode=mode,
            )
            for path in search_response["result"]["path"]
        ]

    def _to_route(
        self,
        path: OdsayResponse,
        *,
        origin: DirectionPlaceData,
        destination: DirectionPlaceData,
        mode: TravelMode,
    ) -> DirectionRouteData:
        info = path["info"]
        lane_response = self.client.load_lane(
            map_object=f"0:0@{info['mapObj']}"
        )
        coordinates = _extract_coordinates(lane_response)

        return DirectionRouteData(
            provider="mock",
            mode=mode,
            origin=origin,
            destination=destination,
            summary=DirectionSummaryData(
                distance_meters=round(info["totalDistance"]),
                duration_seconds=info["totalTime"] * 60,
            ),
            geometry=GeoJsonLineString(coordinates=coordinates),
        )


def _extract_coordinates(response: OdsayResponse) -> list[tuple[float, float]]:
    return [
        (point["x"], point["y"])
        for lane in response["result"]["lane"]
        for section in lane["section"]
        for point in section["graphPos"]
    ]
