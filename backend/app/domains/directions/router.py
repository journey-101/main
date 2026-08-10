from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db_session
from app.domains.directions.schemas import (
    DirectionSearchData,
    DirectionSearchRequest,
)
from app.domains.directions.service import search_directions
from app.domains.health.schemas import SuccessResponse
from app.integrations.directions.base import DirectionsProvider
from app.integrations.directions.provider import get_directions_provider

router = APIRouter()


@router.post("/search", response_model=SuccessResponse[DirectionSearchData])
def search(
    request: DirectionSearchRequest,
    session: Session = Depends(get_db_session),
    provider: DirectionsProvider = Depends(get_directions_provider),
) -> SuccessResponse[DirectionSearchData]:
    return SuccessResponse(data=search_directions(session, request, provider))
