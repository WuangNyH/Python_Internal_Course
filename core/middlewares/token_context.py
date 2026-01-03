from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from security.providers import get_jwt_service


class TokenContextMiddleware(BaseHTTPMiddleware):
    """
    Parse token nhẹ:
    - Nếu có token: verify + decode claims -> request.state.token_claims
    - Nếu token lỗi: request.state.token_error = "expired" | "invalid"
    - Không raise 401/403 tại middleware
    - Không query DB
    """

    async def dispatch(self, request: Request, call_next):
        request.state.token_claims = None
        request.state.token_error = None

        token = _extract_token(request)
        if token:
            jwt_service = get_jwt_service()
            claims, err = jwt_service.decode_access_token(token)
            request.state.token_claims = claims
            request.state.token_error = err  # None | "expired" | "invalid"

        return await call_next(request)


def _extract_token(request: Request) -> str | None:
    # Authorization: Bearer <token>
    auth = request.headers.get("Authorization")
    if auth:
        parts = auth.split(" ", 1)
        if len(parts) == 2 and parts[0].lower() == "bearer":
            token = parts[1].strip()
            return token or None

    # Cookie fallback
    token = request.cookies.get("access_token")
    return token
