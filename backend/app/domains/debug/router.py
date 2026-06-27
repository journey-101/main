from fastapi import APIRouter

from app.domains.debug.schemas import TEST_USER_ID, DebugTestUserData
from app.domains.health.schemas import SuccessResponse

router = APIRouter()


@router.get("/test-user", response_model=SuccessResponse[DebugTestUserData])
def get_test_user() -> SuccessResponse[DebugTestUserData]:
    return SuccessResponse(data=DebugTestUserData(user_id=TEST_USER_ID))
