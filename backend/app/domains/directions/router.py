from typing import Annotated

from fastapi import APIRouter, Depends

from app.db.uow import UnitOfWork, get_uow
from app.domains.directions.schemas import (
    DirectionSearchData,
    DirectionSearchRequest,
)
from app.domains.directions.service import search_directions
from app.domains.health.schemas import SuccessResponse
from app.integrations.directions.base import DirectionsProvider
from app.integrations.directions.provider import get_directions_provider

router = APIRouter()
Uow = Annotated[UnitOfWork, Depends(get_uow)]


@router.post("/search", response_model=SuccessResponse[DirectionSearchData])
def search(
    request: DirectionSearchRequest,
    uow: Uow,
    provider: DirectionsProvider = Depends(get_directions_provider),
) -> SuccessResponse[DirectionSearchData]:
    return SuccessResponse(data=search_directions(uow.places, request, provider))
