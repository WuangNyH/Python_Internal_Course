from typing import TypeVar
from core.trace import trace_id_ctx
from schemas.response.base import SuccessResponse

T = TypeVar("T")


def success_response(
    data: T | None = None,
    *,
    message: str | None = None,
) -> SuccessResponse[T]:
    """
    Helper chuẩn hoá response body cho happy-path:
    - Luôn inject trace_id từ trace_id_ctx (source of truth)
    - Không phụ thuộc Request
    - Dùng cho mọi happy-path HTTP response
    """
    return SuccessResponse(
        success=True,
        data=data,
        message=message,
        trace_id=trace_id_ctx.get() or None,
    )
