from datetime import datetime
from typing import Generic, TypeVar
from pydantic import BaseModel, ConfigDict

T = TypeVar("T")


class SuccessResponse(BaseModel, Generic[T]):
    success: bool = True
    data: T
    message: str | None = None
    trace_id: str | None = None # được tạo ở TraceIdMiddleware


class ErrorResponse(BaseModel):
    success: bool = False
    error_code: str
    message: str
    trace_id: str | None = None
    extra: dict | None = None


class TimestampMixin(BaseModel):
    # Cho phép map trực tiếp từ SQLAlchemy ORM object
    model_config = ConfigDict(from_attributes=True)

    created_at: datetime
    updated_at: datetime