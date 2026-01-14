import uuid
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.types import ASGIApp
from starlette.responses import Response


class RequestIdMiddleware(BaseHTTPMiddleware):
    """
    Execute:
    - Prefer client-provided X-Request-Id if present (gateway / frontend / upstream)
    - Otherwise generate a new UUID4 hex
    - Store in request.state.request_id and echo back in response header
    """

    def __init__(self, app: ASGIApp, header_name: str = "X-Request-Id"):
        super().__init__(app)
        self.header_name = header_name

    async def dispatch(self, request: Request, call_next) -> Response:
        request_id = request.headers.get(self.header_name)
        if not request_id:
            request_id = uuid.uuid4().hex

        request.state.request_id = request_id

        response: Response = await call_next(request)
        response.headers[self.header_name] = request_id
        return response
