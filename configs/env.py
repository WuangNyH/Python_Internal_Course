from functools import lru_cache
from typing import Any

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, SecretStr

from configs.settings.cors import CorsSettings
from configs.settings.security import SecuritySettings, SameSite, JwtSettings, JwtAlgorithm, RefreshCookieSettings, \
    RefreshSessionSettings, CsrfSettings
from core.audit.audit_mode import AuditMode


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    api_prefix: str = Field(default="/api/v1", validation_alias="API_PREFIX")
    environment: str = Field(..., validation_alias="ENVIRONMENT")
    database_url: str = Field(..., validation_alias="DATABASE_URL")

    cors_allow_origins_raw: str | None = Field(default=None, validation_alias="CORS_ALLOW_ORIGINS")
    csrf_enabled: bool = Field(..., validation_alias="CSRF_ENABLED")
    csrf_trusted_origins_raw: str | None = Field(default=None, validation_alias="CSRF_TRUSTED_ORIGINS")

    jwt_algorithm: JwtAlgorithm = Field(default="HS256", validation_alias="JWT_ALGORITHM")
    jwt_secret_key: SecretStr = Field(..., validation_alias="JWT_SECRET_KEY")
    jwt_issuer: str = Field(..., validation_alias="JWT_ISSUER")
    jwt_audience: str = Field(..., validation_alias="JWT_AUDIENCE")
    access_token_expired_minutes: int = Field(default=15, validation_alias="ACCESS_TOKEN_EXPIRED_MINUTES")
    refresh_token_expired_minutes: int = Field(default=20160, validation_alias="REFRESH_SESSION_TTL_MINUTES")
    refresh_token_absolute_expired_minutes: int = Field(default=43200,
                                                        validation_alias="REFRESH_SESSION_ABSOLUTE_TTL_MINUTES")
    refresh_cookie_secure: bool | None = Field(default=None, validation_alias="REFRESH_COOKIE_SECURE")
    refresh_cookie_samesite: SameSite | None = Field(default=None, validation_alias="REFRESH_COOKIE_SAMESITE")
    refresh_cookie_path: str | None = Field(default=None, validation_alias="REFRESH_COOKIE_PATH")
    refresh_cookie_max_age_seconds: int | None = Field(default=None, validation_alias="REFRESH_COOKIE_MAX_AGE_SECONDS")

    security_audit_mode: AuditMode = Field(default=AuditMode.ON, validation_alias="SECURITY_AUDIT_MODE")

    security: SecuritySettings | None = Field(default=None)

    tz: str = Field(default="UTC", validation_alias="TZ")

    pool_size: int = Field(default=10, validation_alias="DB_POOL_SIZE")
    max_overflow: int = Field(default=20, validation_alias="DB_MAX_OVERFLOW")

    # Pydantic hook để mapping CORS origins, JWT, refresh session TTL, refresh cookie settings
    def model_post_init(self, __context):
        # Validate & normalize api_prefix
        if not self.api_prefix.startswith("/"):
            raise ValueError(">>>>> Invalid API_PREFIX: must start with '/'")
        if self.api_prefix != "/" and self.api_prefix.endswith("/"):
            self.api_prefix = self.api_prefix.rstrip("/")

        # Derive refresh cookie path if not provided
        if not self.refresh_cookie_path:
            self.refresh_cookie_path = f"{self.api_prefix}/auth"

        # Build security settings
        jwt_settings = self._build_jwt_settings()
        cors_settings = self._build_cors_settings()
        csrf_settings = self._build_csrf_settings()
        refresh_session_settings = self._build_refresh_session_settings()
        refresh_cookie_settings = self._build_refresh_cookie_settings()

        # Compose full SecuritySettings
        self.security = SecuritySettings(
            jwt=jwt_settings,
            cors=cors_settings,
            csrf=csrf_settings,
            refresh_session=refresh_session_settings,
            refresh_cookie=refresh_cookie_settings,
            audit_mode=self.security_audit_mode,
        )

    def _build_cors_settings(self) -> CorsSettings:
        base = CorsSettings()
        if not self.cors_allow_origins_raw:
            return base

        origins = [o.strip() for o in self.cors_allow_origins_raw.split(",") if o.strip()]
        return base.model_copy(update={"allow_origins": origins})

    def _build_csrf_settings(self) -> CsrfSettings:
        enabled = bool(self.csrf_enabled)

        origins: list[str] = []
        if self.csrf_trusted_origins_raw:
            origins = [o.strip() for o in self.csrf_trusted_origins_raw.split(",") if o.strip()]

        # Fail-fast at boot time
        if enabled and not origins:
            raise ValueError(
                ">>>>> Invalid CSRF config: CSRF_ENABLED=true requires CSRF_TRUSTED_ORIGINS to be set"
            )

        return CsrfSettings(
            enabled=enabled,
            trusted_origins=origins,
        )

    def _build_jwt_settings(self) -> JwtSettings:
        issuer = (self.jwt_issuer or "").strip()
        audience = (self.jwt_audience or "").strip()
        secret = self.jwt_secret_key.get_secret_value().strip()

        if not issuer:
            raise ValueError(">>>>> Invalid JWT config: JWT_ISSUER must not be empty")
        if not audience:
            raise ValueError(">>>>> Invalid JWT config: JWT_AUDIENCE must not be empty")
        if not secret:
            raise ValueError(">>>>> Invalid JWT config: JWT_SECRET_KEY must not be empty")
        if self.access_token_expired_minutes <= 0:
            raise ValueError(">>>>> Invalid JWT config: ACCESS_TOKEN_EXPIRED_MINUTES must be > 0")

        return JwtSettings(
            algorithm=self.jwt_algorithm,
            secret_key=self.jwt_secret_key,
            issuer=issuer,
            audience=audience,
            access_token_ttl_minutes=self.access_token_expired_minutes,
        )

    def _build_refresh_session_settings(self) -> RefreshSessionSettings:
        if self.refresh_token_expired_minutes <= 0:
            raise ValueError(">>>>> Invalid refresh session config: REFRESH_SESSION_TTL_MINUTES must be > 0")
        if self.refresh_token_absolute_expired_minutes <= 0:
            raise ValueError(">>>>> Invalid refresh session config: REFRESH_SESSION_ABSOLUTE_TTL_MINUTES must be > 0")
        if self.refresh_token_absolute_expired_minutes < self.refresh_token_expired_minutes:
            raise ValueError(">>>>> Invalid refresh session config: ABSOLUTE_TTL must be >= TTL (idle timeout)")

        base = RefreshSessionSettings()
        return base.model_copy(
            update={
                "ttl_minutes": self.refresh_token_expired_minutes,
                "absolute_ttl_minutes": self.refresh_token_absolute_expired_minutes,
            }
        )

    def _build_refresh_cookie_settings(self) -> RefreshCookieSettings:
        base = RefreshCookieSettings()

        updates: dict[str, Any] = {}
        if self.refresh_cookie_secure is not None:
            updates["secure"] = self.refresh_cookie_secure
        if self.refresh_cookie_samesite is not None:
            updates["samesite"] = self.refresh_cookie_samesite
        if self.refresh_cookie_path:
            updates["path"] = self.refresh_cookie_path.strip()
        if self.refresh_cookie_max_age_seconds is not None:
            if self.refresh_cookie_max_age_seconds <= 0:
                raise ValueError(">>>>> Invalid cookie config: REFRESH_COOKIE_MAX_AGE_SECONDS must be > 0")
            updates["max_age_seconds"] = self.refresh_cookie_max_age_seconds

        cookie = base.model_copy(update=updates) if updates else base

        # Cross-field validate
        if cookie.samesite == "none" and cookie.secure is not True:
            raise ValueError(">>>>> Invalid cookie policy: SameSite=None requires Secure=true")

        return cookie


@lru_cache
def settings_config() -> Settings:
    # noinspection PyArgumentList
    return Settings()
