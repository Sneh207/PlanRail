from typing import Generic, TypeVar, List, Optional
from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T")

class ErrorDetail(BaseModel):
    code: str
    message: str

class ErrorResponse(BaseModel):
    detail: ErrorDetail

class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    page: int = Field(..., example=1)
    page_size: int = Field(..., example=20)
    total: int = Field(..., example=100)

    model_config = ConfigDict(from_attributes=True)
