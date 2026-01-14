import logging
from http import HTTPStatus

from fastapi import Request
from fastapi.responses import JSONResponse

from core.exceptions.base import BusinessException
from core.http.request_state_keys import RequestStateKeys
from schemas.response.base import ErrorResponse

logger = logging.getLogger(__name__)


def business_exception_handler(
        request: Request,
        exc: BusinessException,
):
    trace_id = getattr(request.state, RequestStateKeys.TRACE_ID, None)

    body = ErrorResponse(
        error_code=exc.error_code,
        message=exc.message,
        trace_id=trace_id,
        extra=exc.extra,
    )

    return JSONResponse(
        status_code=exc.status_code,
        content=body.model_dump(mode="json"),
    )


def unhandled_exception_handler(
        request: Request,
        exc: Exception,
):
    trace_id = getattr(request.state, RequestStateKeys.TRACE_ID, None)

    logger.exception("Unhandled exception", exc_info=exc)

    body = ErrorResponse(
        error_code="INTERNAL_SERVER_ERROR",
        message="Internal server error",
        trace_id=trace_id,
    )

    return JSONResponse(
        status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
        content=body.model_dump(mode="json"),
    )
