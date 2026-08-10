from typing import Protocol


class HealthRepository(Protocol):
    def ping(self) -> int: ...
