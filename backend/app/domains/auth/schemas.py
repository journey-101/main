from pydantic import BaseModel


class CurrentUserData(BaseModel):
    uid: str
    email: str | None
    name: str | None
    provider: str | None
