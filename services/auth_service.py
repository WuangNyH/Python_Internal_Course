from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from fastapi import Request, Response
from sqlalchemy.orm import Session

from configs.settings.security import SecuritySettings
from core.exceptions.auth_exceptions import (
    AuthTokenMissingException,
    InvalidTokenException,
    UserNotFoundOrDisabledException,
)
from repositories.auth_repository import AuthRepository
from repositories.refresh_session_repository import RefreshSessionRepository
from security.cookie_policy import RefreshCookiePolicy
from security.jwt_service import JwtService
from security.password import verify_password
from security.refresh_token import generate_refresh_token, hash_refresh_token


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


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
    ):
        self.auth_repo = auth_repo
        self.refresh_repo = refresh_repo
        self.cookie_policy = cookie_policy
        self.security_settings = security_settings
        self.jwt_service = jwt_service

        if self.security_settings.jwt is None:
            raise RuntimeError("SecuritySettings.jwt is not configured")

        self._access_ttl_minutes = int(self.security_settings.jwt.access_token_ttl_minutes)
        self._refresh_ttl_minutes = int(self.security_settings.refresh_session.ttl_minutes)
        self._refresh_absolute_ttl_minutes = int(self.security_settings.refresh_session.absolute_ttl_minutes)

    def login(
            self,
            db: Session,
            *,
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
            raise InvalidTokenException(token_type="access", reason="invalid_credentials")

        if hasattr(user, "is_active") and not getattr(user, "is_active"):
            raise UserNotFoundOrDisabledException(getattr(user, "id", None))

        if not verify_password(password, getattr(user, "hashed_password", "")):
            raise InvalidTokenException(token_type="access", reason="invalid_credentials")

        user_id = int(getattr(user, "id"))

        _, _, token_version = self.auth_repo.get_authz_snapshot(db, user_id)
        if not token_version:
            raise UserNotFoundOrDisabledException(user_id)

        # Phát hành access token
        access_token = self.jwt_service.create_access_token(
            subject=str(user_id),
            token_version=int(token_version),
        )

        # Phát hành refresh token (opaque) + lưu hash ở DB
        refresh_plain = generate_refresh_token()
        refresh_hash = hash_refresh_token(refresh_plain)

        now = _utcnow()
        refresh_expires_at = now + timedelta(minutes=self._refresh_ttl_minutes)
        refresh_absolute_expires_at = now + timedelta(minutes=self._refresh_absolute_ttl_minutes)

        self.refresh_repo.create_session(
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

        return TokenPairOut(
            access_token=access_token,
            expires_in=self._access_ttl_minutes * 60,
            token_type="Bearer",
        )

    def refresh(
            self,
            db: Session,
            *,
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
            raise AuthTokenMissingException(token_type="refresh")

        old_hash = hash_refresh_token(refresh_plain)

        # Rotate refresh session
        new_plain = generate_refresh_token()
        new_hash = hash_refresh_token(new_plain)

        now = _utcnow()
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
            raise InvalidTokenException(token_type="refresh", reason="session_not_active")

        user_id = int(getattr(session, "user_id"))

        # Load latest authz snapshot (roles/permissions can change)
        _, _, token_version = self.auth_repo.get_authz_snapshot(db, user_id)
        if not token_version:
            raise UserNotFoundOrDisabledException(user_id)

        # Phát hành new access token (latest token_version)
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
            request: Request,
            response: Response,
    ) -> None:
        """
        Logout current device/session:
        - If refresh cookie exists -> revoke that refresh session
        - Clear cookie always
        """
        refresh_plain = request.cookies.get(self.cookie_policy.name)
        if refresh_plain:
            token_hash = hash_refresh_token(refresh_plain)
            # revoke_by_token_hash theo ORM style (bool)
            self.refresh_repo.revoke_by_token_hash(db, token_hash=token_hash)

        self.cookie_policy.clear(response)

    def logout_all(
            self,
            db: Session,
            *,
            user_id: int,
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
        return int(count)
