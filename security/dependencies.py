from typing import Any
from fastapi import Request

from core.exceptions.auth_exceptions import TokenExpiredException, AuthTokenMissingException, InvalidTokenException
from core.http.request_state_keys import RequestStateKeys
from security.principals import CurrentUser
from core.security.types import TokenError, TokenType


def get_token_claims(request: Request) -> dict[str, Any] | None:
    """
    Lấy claims từ TokenContextMiddleware
    Middleware đã decode sẵn vào request.state.token_claims
    """
    return getattr(request.state, RequestStateKeys.TOKEN_CLAIMS, None)


def get_token_error(request: Request) -> str | None:
    """
    token_error: None | "expired" | "invalid" (được set từ middleware). :contentReference[oaicite:8]{index=8}
    """
    return getattr(request.state, RequestStateKeys.TOKEN_ERROR, None)


def require_current_user(
        request: Request,
) -> CurrentUser:
    """
    Dependency bắt buộc khi đăng nhập
    - Không có token -> 401 (missing)
    - Token expired/invalid -> 401
    - Có claims -> build CurrentUser

    Dùng cho endpoint ít nhạy cảm / nội bộ / access token TTL ngắn
    """
    err = get_token_error(request)
    if err == TokenError.EXPIRED:
        raise TokenExpiredException(token_type=TokenType.ACCESS)
    if err == TokenError.INVALID:
        raise InvalidTokenException(token_type=TokenType.ACCESS)

    claims = get_token_claims(request)
    if not claims:
        raise AuthTokenMissingException(token_type=TokenType.ACCESS)

    return CurrentUser.from_claims(claims)
