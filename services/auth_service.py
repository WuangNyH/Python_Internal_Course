import uuid
from dataclasses import dataclass
from datetime import timedelta
from typing import Any

from fastapi import Request, Response
from sqlalchemy.orm import Session

from configs.settings.security import SecuritySettings
from core.audit.audit_actions import AuditAction
from core.context.request_context import RequestContext
from core.exceptions.auth_exceptions import (
    AuthTokenMissingException,
    InvalidTokenException,
    UserNotFoundOrDisabledException,
)
from core.security.types import TokenType
from core.utils.datetime_utils import utcnow
from repositories.auth_repository import AuthRepository
from repositories.refresh_session_repository import RefreshSessionRepository
from security.cookie_policy import RefreshCookiePolicy
from security.jwt_service import JwtService
from security.password import verify_password
from security.refresh_token import generate_refresh_token, hash_refresh_token
from services.audit_log_service import AuditLogService


@dataclass(frozen=True)
class TokenPairOut:
    """
    Service DTO (Service -> Router)
    - access_token trả trong body
    - refresh_token set trong cookie (HttpOnly) => KHÔNG đưa vào body
    """
    access_token: str
    expires_in: int  # seconds
    token_type: str = "Bearer"


class AuthService:
    """
    Execute:
    - login: verify credentials -> issue access + refresh cookie + store refresh session
    - refresh: validate+rotate refresh session -> issue new access + new refresh cookie
    - logout: revoke refresh session -> clear refresh cookie
    - logout_all: revoke all sessions for user -> clear refresh cookie
    """

    def __init__(
            self,
            *,
            auth_repo: AuthRepository,
            refresh_repo: RefreshSessionRepository,
            cookie_policy: RefreshCookiePolicy,
            security_settings: SecuritySettings,
            jwt_service: JwtService,
            audit_log_service: AuditLogService,
    ):
        self.auth_repo = auth_repo
        self.refresh_repo = refresh_repo
        self.cookie_policy = cookie_policy
        self.security_settings = security_settings
        self.jwt_service = jwt_service
        self.audit_log_service = audit_log_service

        self._access_ttl_minutes = int(self.security_settings.jwt.access_token_ttl_minutes)
        self._refresh_ttl_minutes = int(self.security_settings.refresh_session.ttl_minutes)
        self._refresh_absolute_ttl_minutes = int(self.security_settings.refresh_session.absolute_ttl_minutes)

    def login(
            self,
            db: Session,
            *,
            ctx: RequestContext,
            request: Request,
            response: Response,
            email: str,
            password: str,
    ) -> TokenPairOut:
        """
        Execute:
        - Load user credentials by email
        - Verify password
        - Load authz snapshot (roles, permissions, token_version)
        - Issue access token (JWT)
        - Issue refresh token (opaque) + store hashed session + set cookie
        """
        user = self.auth_repo.get_user_credentials_by_email(db, email)

        if not user:
            self._audit_login_failed(db, ctx=ctx, reason="invalid_credentials")
            raise InvalidTokenException(TokenType.ACCESS, reason="invalid_credentials")

        if hasattr(user, "is_active") and not getattr(user, "is_active"):
            self._audit_login_failed(db, ctx=ctx, reason="user_disabled")
            raise UserNotFoundOrDisabledException(getattr(user, "id", None))

        if not verify_password(password, getattr(user, "hashed_password", "")):
            self._audit_login_failed(db, ctx=ctx, reason="invalid_credentials")
            raise InvalidTokenException(TokenType.ACCESS, reason="invalid_credentials")

        user_id = getattr(user, "id")

        _, _, token_version = self.auth_repo.get_authz_snapshot(db, user_id)
        if not token_version:
            # user not found/disabled snapshot
            self._audit_login_failed(db, ctx=ctx, reason="user_disabled")
            raise UserNotFoundOrDisabledException(user_id)

        # Issue access token
        access_token = self.jwt_service.create_access_token(
            subject=str(user_id),
            token_version=int(token_version),
        )

        # Issue refresh token (opaque) + store hash in DB
        refresh_plain = generate_refresh_token()
        refresh_hash = hash_refresh_token(refresh_plain)

        now = utcnow()
        refresh_expires_at = now + timedelta(minutes=self._refresh_ttl_minutes)
        refresh_absolute_expires_at = now + timedelta(minutes=self._refresh_absolute_ttl_minutes)

        session = self.refresh_repo.create_session(
            db,
            user_id=user_id,
            token_hash=refresh_hash,
            expires_at=refresh_expires_at,
            absolute_expires_at=refresh_absolute_expires_at,
            user_agent=request.headers.get("User-Agent"),
            ip_address=request.client.host if request.client else None,
        )

        # Set refresh cookie
        self.cookie_policy.set(response, refresh_plain)

        # Audit login success (no tokens, no secrets)
        self.audit_log_service.log_event(
            db,
            action=AuditAction.AUTH_LOGIN_SUCCESS,
            entity_type="User",
            entity_id=str(user_id),
            actor_user_id=user_id,
            after={
                "status": "success",
                "method": "password",
                "token_version": int(token_version),
                "refresh_session_id": str(getattr(session, "id", "")) if getattr(session, "id", None) else None,
            },
            **self._audit_ctx_kwargs(ctx),
        )

        return TokenPairOut(
            access_token=access_token,
            expires_in=self._access_ttl_minutes * 60,
            token_type="Bearer",
        )

    def refresh(
            self,
            db: Session,
            *,
            ctx: RequestContext,
            request: Request,
            response: Response,
    ) -> TokenPairOut:
        """
        Execute:
        - Read refresh token from cookie
        - Hash -> rotate refresh session
        - Load authz snapshot (roles, permissions, token_version)
        - Issue new access token
        - Set new refresh cookie (rotated)
        """
        refresh_plain = request.cookies.get(self.cookie_policy.name)
        if not refresh_plain:
            self._audit_refresh_failed(db, ctx=ctx, reason="missing_refresh_cookie")
            raise AuthTokenMissingException(TokenType.REFRESH)

        old_hash = hash_refresh_token(refresh_plain)

        # Rotate refresh session
        new_plain = generate_refresh_token()
        new_hash = hash_refresh_token(new_plain)

        now = utcnow()
        new_expires_at = now + timedelta(minutes=self._refresh_ttl_minutes)

        session = self.refresh_repo.rotate_session(
            db,
            old_token_hash=old_hash,
            new_token_hash=new_hash,
            new_expires_at=new_expires_at,
            now=now,
        )
        if not session:
            # revoked/expired/unknown
            self._audit_refresh_failed(db, ctx=ctx, reason="session_not_active")
            raise InvalidTokenException(TokenType.REFRESH, reason="session_not_active")

        user_id = getattr(session, "user_id")

        # Load latest authz snapshot (roles/permissions can change)
        _, _, token_version = self.auth_repo.get_authz_snapshot(db, user_id)
        if not token_version:
            self._audit_refresh_failed(db, ctx=ctx, reason="user_disabled")
            raise UserNotFoundOrDisabledException(user_id)

        # Issue new access token (latest token_version)
        access_token = self.jwt_service.create_access_token(
            subject=str(user_id),
            token_version=int(token_version),
        )

        # Set rotated refresh cookie
        self.cookie_policy.set(response, new_plain)

        return TokenPairOut(
            access_token=access_token,
            expires_in=self._access_ttl_minutes * 60,
            token_type="Bearer",
        )

    def logout(
            self,
            db: Session,
            *,
            ctx: RequestContext,
            request: Request,
            response: Response,
    ) -> None:
        """
        Logout current device/session:
        - If refresh cookie exists -> revoke that refresh session
        - Clear cookie always

        Audit: AUTH_LOGOUT
        - If session active: log actor_user_id + refresh_session_id
        - If not resolvable: log anonymous logout
        """
        refresh_plain = request.cookies.get(self.cookie_policy.name)

        revoked = False
        resolved_user_id: uuid.UUID | None = None
        resolved_session_id: str | None = None

        if refresh_plain:
            token_hash = hash_refresh_token(refresh_plain)

            # Try to resolve active session -> get user_id for audit
            session = self.refresh_repo.get_active_by_token_hash(
                db,
                token_hash=token_hash,
                for_update=True,
            )
            if session:
                resolved_user_id = getattr(session, "user_id", None)
                sid = getattr(session, "id", None)
                resolved_session_id = str(sid) if sid is not None else None

                revoked = self.refresh_repo.revoke_by_token_hash(db, token_hash=token_hash)
            else:
                # Not active/expired/revoked -> still clear cookie, still audit attempt
                revoked = False

        self.cookie_policy.clear(response)

        self.audit_log_service.log_event(
            db,
            action=AuditAction.AUTH_LOGOUT,
            entity_type="RefreshSession",
            entity_id=resolved_session_id or "unknown",
            actor_user_id=resolved_user_id,
            after={"status": "success", "revoked": bool(revoked)},
            **self._audit_ctx_kwargs(ctx),
        )

    def logout_all(
            self,
            db: Session,
            *,
            ctx: RequestContext,
            user_id: uuid.UUID,
            response: Response,
    ) -> int:
        """
        Logout all devices:
        - Revoke all refresh sessions for user
        - Clear cookie
        - Return number of revoked sessions
        """
        count = self.refresh_repo.revoke_all_for_user(db, user_id=user_id)
        self.cookie_policy.clear(response)

        actor_user_id = ctx.current_user.user_id if ctx.current_user else None

        self.audit_log_service.log_event(
            db,
            action=AuditAction.AUTH_REVOKE_ALL_SESSIONS,
            entity_type="User",
            entity_id=str(user_id),
            actor_user_id=actor_user_id,
            after={"revoked_sessions": count},
            **self._audit_ctx_kwargs(ctx),
        )

        return int(count)

    # ===== Audit helpers =====
    def _audit_ctx_kwargs(self, ctx: RequestContext) -> dict[str, Any]:
        return {
            "request_id": ctx.request_id,
            "trace_id": ctx.trace_id,
            "ip": ctx.ip,
            "user_agent": ctx.user_agent,
        }

    def _audit_login_failed(self, db: Session, *, ctx: RequestContext, reason: str) -> None:
        """
        Policy: do NOT log email/user_id on login failed.
        """
        self.audit_log_service.log_event(
            db,
            action=AuditAction.AUTH_LOGIN_FAILED,
            entity_type="Auth",
            entity_id="login",
            actor_user_id=None,
            after={"status": "failed", "reason": reason},
            **self._audit_ctx_kwargs(ctx),
        )

    def _audit_refresh_failed(self, db: Session, *, ctx: RequestContext, reason: str) -> None:
        """
        Policy: do NOT log refresh success. Only log refresh failures.
        Do NOT log user_id here.
        """
        self.audit_log_service.log_event(
            db,
            action=AuditAction.AUTH_REFRESH_FAILED,
            entity_type="Auth",
            entity_id="refresh",
            actor_user_id=None,
            after={"status": "failed", "reason": reason},
            **self._audit_ctx_kwargs(ctx),
        )
