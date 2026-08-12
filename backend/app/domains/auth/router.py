from typing import Annotated

from fastapi import APIRouter, Depends

from app.core.auth import CurrentUser, get_current_user
from app.domains.auth.schemas import CurrentUserData
from app.domains.health.schemas import SuccessResponse

router = APIRouter()


@router.get("/me", response_model=SuccessResponse[CurrentUserData])
def get_me(
    user: Annotated[CurrentUser, Depends(get_current_user)],
) -> SuccessResponse[CurrentUserData]:
    return SuccessResponse(data=CurrentUserData(**user.__dict__))
