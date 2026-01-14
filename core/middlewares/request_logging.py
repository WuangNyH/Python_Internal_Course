import logging
import time
import uuid
from dataclasses import dataclass
from typing import Any

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import ASGIApp

from core.http.request_state_keys import RequestStateKeys
from security.principals import CurrentUser

logger = logging.getLogger("access")


@dataclass(frozen=True)
class RequestLogConfig:
    log_start: bool = True
    log_end: bool = True

    skip_paths: tuple[str, ...] = ("/health", "/metrics", "/docs", "/openapi.json")
    skip_path_prefixes: tuple[str, ...] = ()

    include_request_id: bool = True
    include_trace_id: bool = True
    include_user_id: bool = True

    include_query_string: bool = False

    include_headers: bool = False
    header_allowlist: tuple[str, ...] = ("user-agent", "x-forwarded-for")

    log_exception: bool = True


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp, config: RequestLogConfig | None = None):
        super().__init__(app)
        self.cfg = config or RequestLogConfig(include_query_string=True)

    def _should_skip(self, path: str) -> bool:
        if path in self.cfg.skip_paths:
            return True
        return any(path.startswith(prefix) for prefix in self.cfg.skip_path_prefixes)

    def _get_ids(self, request: Request) -> dict[str, Any]:
        extra: dict[str, Any] = {}
        if self.cfg.include_request_id:
            extra["request_id"] = getattr(
                request.state, RequestStateKeys.REQUEST_ID, None)
        if self.cfg.include_trace_id:
            extra["trace_id"] = getattr(
                request.state, RequestStateKeys.TRACE_ID, None)
        return extra

    def _get_user_id(self, request: Request) -> uuid.UUID | None:
        cu = getattr(request.state, RequestStateKeys.CURRENT_USER, None)
        if isinstance(cu, CurrentUser):
            return cu.user_id
        return None

    def _get_client_ip(self, request: Request) -> str | None:
        # ưu tiên proxy header
        xff = request.headers.get("x-forwarded-for")
        if xff:
            return xff.split(",")[0].strip()
        return request.client.host if request.client else None

    def _safe_headers(self, request: Request) -> dict[str, str] | None:
        if not self.cfg.include_headers:
            return None
        allow = {h.lower() for h in self.cfg.header_allowlist}
        headers: dict[str, str] = {}
        for k, v in request.headers.items():
            if k.lower() in allow:
                headers[k.lower()] = v
        return headers or None

    def _build_base_extra(self, request: Request) -> dict[str, Any]:
        path = request.url.path

        base_extra: dict[str, Any] = {
            **self._get_ids(request),
            "http_method": request.method,
            "path": path,
        }

        if self.cfg.include_query_string and request.url.query:
            base_extra["query"] = request.url.query

        headers = self._safe_headers(request)
        if headers is not None:
            base_extra["headers"] = headers

        if self.cfg.include_user_id:
            base_extra["user_id"] = self._get_user_id(request)

        base_extra["client_ip"] = self._get_client_ip(request)

        return base_extra

    def _log_start(self, base_extra: dict[str, Any]) -> None:
        if not self.cfg.log_start:
            return

        client_ip = base_extra.get("client_ip")
        method = base_extra.get("http_method")
        path = base_extra.get("path")

        if self.cfg.include_query_string and base_extra.get("query"):
            path_with_query = f"{path}?{base_extra.get('query')}"
        else:
            path_with_query = path

        logger.info(
            ">>>>>>>> http.request.start %s %s %s",
            client_ip,
            method,
            path_with_query,
            extra={
                **base_extra,
                "req_phase": "start", # override color
            },
        )

    def _log_end(
            self,
            *,
            base_extra: dict[str, Any],
            start_perf: float,
            response: Response | None,
            exc: BaseException | None,
    ) -> None:
        if not self.cfg.log_end:
            return

        duration_ms = (time.perf_counter() - start_perf) * 1000.0
        status_code = getattr(response, "status_code", 500)

        end_extra: dict[str, Any] = {
            **base_extra,
            "status_code": status_code,
            "duration_ms": round(duration_ms, 2),
        }

        if exc is not None and self.cfg.log_exception:
            end_extra["error_class"] = exc.__class__.__name__

        logger.info(
            "%s duration_ms=%.2f http.request.end <<<<<<<<\n",
            status_code,
            duration_ms,
            extra={
                **end_extra,
                "req_phase": "end",
            },
        )

    async def dispatch(self, request: Request, call_next) -> Response:
        path = request.url.path
        skip = self._should_skip(path)

        start_perf = time.perf_counter()
        base_extra = self._build_base_extra(request)

        if not skip:
            self._log_start(base_extra)

        response: Response | None = None
        exc: BaseException | None = None

        try:
            response = await call_next(request)
            return response
        except BaseException as e:
            exc = e
            raise
        finally:
            status_code = getattr(response, "status_code", 500)
            should_log_end = (not skip) or exc is not None or status_code >= 400
            if should_log_end:
                self._log_end(
                    base_extra=base_extra,
                    start_perf=start_perf,
                    response=response,
                    exc=exc,
                )
