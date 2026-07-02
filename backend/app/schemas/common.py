from typing import Generic, TypeVar

from pydantic import BaseModel, Field

DataT = TypeVar("DataT")


class ResponseMeta(BaseModel):
    request_id: str


class ResponseEnvelope(BaseModel, Generic[DataT]):
    data: DataT
    meta: ResponseMeta


class ErrorDetail(BaseModel):
    field: str
    issue: str


class ErrorModel(BaseModel):
    code: str
    message: str
    request_id: str
    details: list[ErrorDetail] = Field(default_factory=list)


class ErrorResponse(BaseModel):
    error: ErrorModel
