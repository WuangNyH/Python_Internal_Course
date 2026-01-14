from functools import lru_cache

from configs.env import settings_config
from repositories.audit_log_repository import AuditLogRepository
from repositories.refresh_session_repository import RefreshSessionRepository
from services.user_service import UserService
from services.audit_log_service import AuditLogService
from repositories.user_repository import UserRepository


@lru_cache
def get_audit_log_service() -> AuditLogService:
    # AuditLogService stateless => cache OK
    settings = settings_config()
    mode = settings.security.audit_mode

    return AuditLogService(
        audit_log_repo=AuditLogRepository(),
        audit_mode=mode,
    )


@lru_cache
def get_user_service() -> UserService:
    # Điều kiện: UserService phải là stateless => cache OK
    return UserService(
        user_repo=UserRepository(),
        refresh_session_repo=RefreshSessionRepository(),
        audit_log_service=get_audit_log_service(),
    )
