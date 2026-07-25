from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db_session
from app.domains.directions.schemas import (
    DirectionSearchData,
    DirectionSearchRequest,
)
from app.domains.directions.service import search_directions
from app.domains.health.schemas import SuccessResponse

router = APIRouter()


@router.post("/search", response_model=SuccessResponse[DirectionSearchData])
def search(
    request: DirectionSearchRequest,
    session: Session = Depends(get_db_session),
) -> SuccessResponse[DirectionSearchData]:
    return SuccessResponse(data=search_directions(session, request))
