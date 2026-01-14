import logging
from typing import Callable

from fastapi import Depends, Request
from sqlalchemy.orm import Session

from core.exceptions.auth_exceptions import InvalidTokenException, UserNotFoundOrDisabledException, ForbiddenException
from core.security.types import TokenType
from security.dependencies import require_current_user
from security.principals import CurrentUser
from repositories.auth_repository import AuthRepository
from dependencies.db import get_db

logger = logging.getLogger(__name__)


def get_auth_repository() -> AuthRepository:
    return AuthRepository()


def require_current_user_verified(
        request: Request,
        db: Session = Depends(get_db),
        user: CurrentUser = Depends(require_current_user),
        auth_repo: AuthRepository = Depends(get_auth_repository),
) -> CurrentUser:
    """
    Verified principal (enterprise):
    - Input: CurrentUser lấy từ claims (require_current_user)
    - DB snapshot: (roles, permissions, token_version)
    - Verify token_version: claim_tv phải == db_tv
    - Return CurrentUser "fresh" (roles/permissions lấy theo DB)
    """
    # Parse user_id từ principal (sub)
    try:
        user_id = user.user_id
    except (TypeError, ValueError):
        logger.warning(
            "auth.invalid_subject",
            extra={
                "sub": getattr(user, "user_id", None),
                "path": request.url.path,
                "method": request.method,
            },
        )
        # Access token đã decode được nhưng claim sub sai format -> invalid access token
        raise InvalidTokenException(TokenType.ACCESS, reason="invalid_subject")

    # DB snapshot (roles/perms/token_version)
    roles, permissions, db_token_version = auth_repo.get_authz_snapshot(db, user_id)

    # user not found/disabled/deleted (repo return token_version=0 để báo invalid)
    if not db_token_version:
        logger.warning(
            "auth.user_not_found_or_disabled",
            extra={
                "user_id": user_id,
                "path": request.url.path,
                "method": request.method,
            },
        )
        raise UserNotFoundOrDisabledException(user_id)

    # token_version check (revoke-all)
    claim_tv = int(getattr(user, "token_version", 1))
    if claim_tv != int(db_token_version):
        # token bị revoke: coi như token invalid
        logger.info(  # đây không phải system error, thường log INFO là đủ (token bị revoke là event hợp lệ)
            "auth.token_revoked",
            extra={
                "user_id": user_id,
                "claim_tv": claim_tv,
                "db_tv": int(db_token_version),
                "path": request.url.path,
                "method": request.method,
            },
        )
        raise InvalidTokenException(TokenType.ACCESS, reason="token_revoked")

    # Return principal fresh theo DB (roles/perms có thể đã thay đổi)
    return CurrentUser(
        user_id=user_id,
        roles=list(roles),
        permissions=set(permissions),
        token_version=int(db_token_version),
        tenant_id=getattr(user, "tenant_id", None),
    )


def require_permissions(*required: str) -> Callable[[CurrentUser], CurrentUser]:
    """
    Factory dependency: require_permissions("student:read", "student:write")
    - Nếu thiếu bất kỳ permission nào -> 403
    """
    required_set = set(required)

    def _dep(user: CurrentUser = Depends(require_current_user_verified)) -> CurrentUser:
        # Các permission được yêu cầu nhưng user không có
        # dùng toán tử '-' với set
        missing = sorted(required_set - user.permissions)

        if missing:
            raise ForbiddenException(required=missing)
        return user

    return _dep


def require_roles(*required: str) -> Callable[[CurrentUser], CurrentUser]:
    """
    Factory dependency: require_roles("admin", "manager")
    - Nếu user không có bất kỳ role nào trong required -> 403
    """
    required_set = set(required)

    def _dep(user: CurrentUser = Depends(require_current_user_verified)) -> CurrentUser:
        user_roles = set(user.roles)

        # user phải có ÍT NHẤT 1 role trong required
        if user_roles.isdisjoint(required_set):
            raise ForbiddenException(required=[f"role:{r}" for r in sorted(required_set)])

        return user

    return _dep
