from fastapi import FastAPI

from configs.env import settings_config
from controllers.health_controller import health_router
from controllers.student_controller import student_router
from controllers.user_controller import user_router
from core.app_logging import setup_logging
from core.exceptions.base import BusinessException
from core.exceptions.exception_handlers import business_exception_handler, unhandled_exception_handler
from middlewares.db_session import DBSessionMiddleware
from middlewares.trace_id import TraceIdMiddleware

app = FastAPI()

settings = settings_config()
setup_logging(sql_echo=(settings.environment == "DEV"))

# Đăng ký router
app.include_router(health_router, tags=["Health"])
app.include_router(user_router, prefix="/users", tags=["Users"])
app.include_router(student_router, prefix="/students", tags=["Students"])

# Đăng ký Exception Handler => thứ tự bắt buộc
app.add_exception_handler(BusinessException, business_exception_handler)
app.add_exception_handler(Exception, unhandled_exception_handler)

# Đăng ký middleware => thứ tự quan trọng
app.add_middleware(DBSessionMiddleware)
app.add_middleware(TraceIdMiddleware)  # add sau để bọc ngoài
