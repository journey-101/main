from typing import Protocol


class UserRepository(Protocol):
    def ensure(self, firebase_uid: str) -> None: ...
