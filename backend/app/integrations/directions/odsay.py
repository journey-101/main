from typing import Any, Protocol


OdsayResponse = dict[str, Any]


class OdsayClient(Protocol):
    def search_pub_trans_path_t(
        self,
        *,
        sx: float,
        sy: float,
        ex: float,
        ey: float,
    ) -> OdsayResponse: ...

    def load_lane(self, *, map_object: str) -> OdsayResponse: ...
