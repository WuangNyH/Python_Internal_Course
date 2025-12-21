from http import HTTPStatus

from core.exceptions.base import BusinessException


class AuthTokenMissingException(BusinessException):
    def __init__(self):
        super().__init__(
            message="Authentication token is missing",
            error_code="AUTH_TOKEN_MISSING",
            status_code=HTTPStatus.UNAUTHORIZED,
        )


class InvalidTokenException(BusinessException):
    def __init__(self):
        super().__init__(
            message="Invalid authentication token",
            error_code="AUTH_TOKEN_INVALID",
            status_code=HTTPStatus.UNAUTHORIZED,
        )


class TokenExpiredException(BusinessException):
    def __init__(self):
        super().__init__(
            message="Authentication token has expired",
            error_code="AUTH_TOKEN_EXPIRED",
            status_code=HTTPStatus.UNAUTHORIZED,
        )


class UserNotFoundOrDisabledException(BusinessException):
    def __init__(self, user_id: int | str | None):
        super().__init__(
            message="User is not found or disabled",
            error_code="AUTH_USER_INVALID",
            status_code=HTTPStatus.UNAUTHORIZED,
            extra={"user_id": user_id},
        )


class ForbiddenException(BusinessException):
    def __init__(self, required: list[str] | None = None):
        super().__init__(
            message="You do not have permission to perform this action",
            error_code="FORBIDDEN",
            status_code=HTTPStatus.FORBIDDEN,
            extra={"required_permissions": required or []},
        )
