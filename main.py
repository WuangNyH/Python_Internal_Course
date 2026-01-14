from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from configs.env import settings_config
from controllers.auth_controller import auth_router
from controllers.health_controller import health_router
from controllers.student_controller import student_router
from controllers.user_controller import user_router
from core.app_logging import setup_logging
from core.exceptions.base import BusinessException
from core.exceptions.exception_handlers import business_exception_handler, unhandled_exception_handler
from core.middlewares.db_session import DBSessionMiddleware
from core.middlewares.request_id import RequestIdMiddleware
from core.middlewares.request_logging import RequestLoggingMiddleware
from core.middlewares.token_context import TokenContextMiddleware
from core.middlewares.trace_id import TraceIdMiddleware

app = FastAPI(
    swagger_ui_parameters={"persistAuthorization": True}
)

settings = settings_config()
setup_logging(sql_echo=(settings.environment == "DEV"))

# Đăng ký router
app.include_router(health_router, tags=["Health"])
app.include_router(
    auth_router, prefix=f"{settings.api_prefix}/auth", tags=["Auth"])
app.include_router(
    user_router, prefix=f"{settings.api_prefix}/users", tags=["Users"])
app.include_router(
    student_router, prefix=f"{settings.api_prefix}/students", tags=["Students"])

# Đăng ký Exception Handler => thứ tự bắt buộc
app.add_exception_handler(BusinessException, business_exception_handler)
app.add_exception_handler(Exception, unhandled_exception_handler)

# Đăng ký middleware => thứ tự quan trọng
app.add_middleware(DBSessionMiddleware)
app.add_middleware(TokenContextMiddleware)
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(TraceIdMiddleware)
app.add_middleware(RequestIdMiddleware)  # add sau để bọc ngoài

# CORS middleware (OUTERMOST)
cors = settings.security.cors
if cors.enabled:
    # Guard: khi dùng cookie (allow_credentials=True) thì không được phép allow_origins="*"
    if cors.allow_credentials and ("*" in cors.allow_origins):
        raise RuntimeError(
            "CORS misconfig: allow_credentials=True cannot be used with allow_origins='*'"
        )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors.allow_origins,
        allow_credentials=cors.allow_credentials,
        allow_methods=cors.allow_methods,
        allow_headers=cors.allow_headers,
        expose_headers=cors.expose_headers,
        max_age=cors.max_age,
    )
