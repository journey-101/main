from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query

from app.db.uow import UnitOfWork, get_uow
from app.domains.health.schemas import SuccessResponse
from app.domains.places.schemas import (
    PlaceDetailData,
    PlaceSearchData,
    PlaceSearchQuery,
)
from app.domains.places.service import (
    get_place_detail,
    search_places as search_places_service,
)

router = APIRouter()
Uow = Annotated[UnitOfWork, Depends(get_uow)]


@router.get("/search", response_model=SuccessResponse[PlaceSearchData])
def search_places(
    query: Annotated[PlaceSearchQuery, Query()], uow: Uow
) -> SuccessResponse[PlaceSearchData]:
    return SuccessResponse(data=search_places_service(uow.places, query))


@router.get("/{place_id}", response_model=SuccessResponse[PlaceDetailData])
def get_place(place_id: UUID, uow: Uow) -> SuccessResponse[PlaceDetailData]:
    return SuccessResponse(data=get_place_detail(uow.places, place_id))
