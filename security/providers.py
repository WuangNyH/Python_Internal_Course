from functools import lru_cache

from configs.env import settings_config
from repositories.auth_repository import AuthRepository
from repositories.refresh_session_repository import RefreshSessionRepository
from security.cookie_policy import RefreshCookiePolicy
from security.jwt_service import JwtService
from services.auth_service import AuthService


@lru_cache
def get_refresh_cookie_policy() -> RefreshCookiePolicy:
    settings = settings_config()
    return RefreshCookiePolicy(settings.security.refresh_cookie)


@lru_cache
def get_jwt_service() -> JwtService:
    settings = settings_config()
    return JwtService(settings.security.jwt)


@lru_cache
def get_auth_repository() -> AuthRepository:
    # Repo stateless: để cache
    return AuthRepository()


@lru_cache
def get_refresh_session_repository() -> RefreshSessionRepository:
    # Repo stateless: để cache
    return RefreshSessionRepository()


@lru_cache
def get_auth_service() -> AuthService:
    settings = settings_config()
    return AuthService(
        auth_repo=get_auth_repository(),
        refresh_repo=get_refresh_session_repository(),
        cookie_policy=get_refresh_cookie_policy(),
        security_settings=settings.security,
        jwt_service=get_jwt_service(),
    )
