import uuid
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import ASGIApp

from core.trace import trace_id_ctx


class TraceIdMiddleware(BaseHTTPMiddleware):
    """
    Execute:
    - Prefer upstream X-Trace-Id (gateway / service mesh / tracing system)
    - Otherwise generate a new trace id
    - Store in request.state.trace_id and echo back
    - Set contextvar for logging correlation
    """

    def __init__(self, app: ASGIApp, header_name: str = "X-Trace-Id"):
        super().__init__(app)
        self.header_name = header_name

    async def dispatch(self, request: Request, call_next) -> Response:
        # Nếu clien ko gửi => tự generate trace_id mới cho mỗi request
        trace_id = request.headers.get(self.header_name)
        if not trace_id:
            trace_id = uuid.uuid4().hex

        # Gắn vào request.state để controller/service dùng
        request.state.trace_id = trace_id

        # Gắn vào contextvar để logging tự động lấy được
        token = trace_id_ctx.set(trace_id)
        try:
            response = await call_next(request)

            # Trả trace_id cho client qua header
            response.headers[self.header_name] = trace_id
            return response
        finally:
            # Reset context để tránh leak sang request khác
            trace_id_ctx.reset(token)
