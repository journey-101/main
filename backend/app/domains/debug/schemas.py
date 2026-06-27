from uuid import UUID

from pydantic import BaseModel


TEST_USER_ID = UUID("00000000-0000-0000-0000-000000000000")


class DebugTestUserData(BaseModel):
    user_id: UUID
