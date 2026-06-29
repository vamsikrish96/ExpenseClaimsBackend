from datetime import datetime, timezone
from typing import Any, Optional, Generic, TypeVar
from pydantic import BaseModel, Field

T = TypeVar("T")


class PaginationInfo(BaseModel):
    offset: int = Field(..., ge=0)
    limit: int = Field(..., gt=0)
    total: int = Field(..., ge=0)
    has_more: bool


class SuccessResponse(BaseModel, Generic[T]):
    success: bool = True
    data: Optional[T] = None
    message: Optional[str] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class SuccessListResponse(BaseModel, Generic[T]):
    success: bool = True
    data: list[T]
    pagination: PaginationInfo
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ErrorResponse(BaseModel):
    success: bool = False
    error: str
    message: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    details: Optional[dict] = None
