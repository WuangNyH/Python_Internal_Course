from typing import Generic, TypeVar
from pydantic import BaseModel

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