from typing import Generic, TypeVar

from pydantic import BaseModel

DataT = TypeVar("DataT")


class ErrorData(BaseModel):
    code: str
    message: str


class SuccessResponse(BaseModel, Generic[DataT]):
    success: bool = True
    data: DataT


class ErrorResponse(BaseModel):
    success: bool = False
    error: ErrorData


class HealthData(BaseModel):
    status: str
    service: str


class DbHealthData(BaseModel):
    status: str
    db: str
    result: int
