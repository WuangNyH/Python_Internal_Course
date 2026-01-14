import uuid
from http import HTTPStatus

from core.exceptions.base import BusinessException
from core.security.types import TokenType


def _error_code(base: str, token_type: TokenType) -> str:
    """
    base: 'TOKEN_MISSING' | 'TOKEN_INVALID' | 'TOKEN_EXPIRED'
    => 'AUTH_ACCESS_TOKEN_MISSING' | 'AUTH_REFRESH_TOKEN_INVALID' | 'AUTH_TOKEN_EXPIRED'
    """
    if token_type == TokenType.ACCESS:
        prefix = "AUTH_ACCESS"
    elif token_type == TokenType.REFRESH:
        prefix = "AUTH_REFRESH"
    else:
        prefix = "AUTH"
    return f"{prefix}_{base}"

def _extra_token_type(token_type: TokenType) -> dict[str, str]:
    """
    Always serialize enum to string for logs/JSON response payload
    """
    return {"token_type": str(token_type)}


class AuthTokenMissingException(BusinessException):
    def __init__(self, token_type: TokenType = TokenType.UNKNOWN):
        super().__init__(
            message="Authentication token is missing",
            error_code=_error_code("TOKEN_MISSING", token_type),
            status_code=HTTPStatus.UNAUTHORIZED,
            extra=_extra_token_type(token_type),
        )


class InvalidTokenException(BusinessException):
    def __init__(self, token_type: TokenType = TokenType.UNKNOWN, *, reason: str | None = None):
        extra = _extra_token_type(token_type)
        if reason:
            extra["reason"] = reason

        super().__init__(
            message="Authentication token is invalid",
            error_code=_error_code("TOKEN_INVALID", token_type),
            status_code=HTTPStatus.UNAUTHORIZED,
            extra=extra,
        )


class TokenExpiredException(BusinessException):
    def __init__(self, token_type: TokenType = TokenType.UNKNOWN):
        super().__init__(
            message="Authentication token has expired",
            error_code=_error_code("TOKEN_EXPIRED", token_type),
            status_code=HTTPStatus.UNAUTHORIZED,
            extra=_extra_token_type(token_type),
        )


class UserNotFoundOrDisabledException(BusinessException):
    def __init__(self, user_id: uuid.UUID | str | None):
        super().__init__(
            message="User is not found or disabled",
            error_code="AUTH_USER_INVALID",
            status_code=HTTPStatus.UNAUTHORIZED,
            extra={"user_id": str(user_id) if user_id else None},
        )


class ForbiddenException(BusinessException):
    def __init__(self, required: list[str] | None = None):
        super().__init__(
            message="You do not have permission to perform this action",
            error_code="AUTH_PERMISSION_DENIED",
            status_code=HTTPStatus.FORBIDDEN,
            extra={"required_permissions": required or []},
        )
