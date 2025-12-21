import uuid
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from core.trace import trace_id_ctx

TRACE_HEADER = "X-Trace-Id"


class TraceIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        # Luôn generate trace_id mới cho mỗi request
        trace_id = str(uuid.uuid4())

        # Gắn vào request.state để controller/service dùng
        request.state.trace_id = trace_id

        # Gắn vào contextvar để logging tự động lấy được
        token = trace_id_ctx.set(trace_id)
        try:
            response = await call_next(request)
        finally:
            # Reset context để tránh leak sang request khác
            trace_id_ctx.reset(token)

        # Trả trace_id cho client qua header
        response.headers[TRACE_HEADER] = trace_id
        return response
