from http import HTTPStatus

from core.exceptions.base import BusinessException


class CsrfOriginRejectedException(BusinessException):
    """
    403 - Cookie-based endpoint but request origin is not allowed.
    """

    def __init__(self, *, origin: str | None, referer: str | None, allowed: list[str]):
        super().__init__(
            message="CSRF protection: origin is not allowed",
            error_code="AUTH_CSRF_ORIGIN_REJECTED",
            status_code=HTTPStatus.FORBIDDEN,
            extra={
                "origin": origin,
                "referer": referer,
                "allowed_origins": allowed,
            },
        )


class CsrfMissingOriginException(BusinessException):
    """
    403 - Cookie-based endpoint but both Origin and Referer are missing.
    """

    def __init__(self, *, allowed: list[str]):
        super().__init__(
            message="CSRF protection: missing origin",
            error_code="AUTH_CSRF_MISSING_ORIGIN",
            status_code=HTTPStatus.FORBIDDEN,
            extra={"allowed_origins": allowed},
        )
