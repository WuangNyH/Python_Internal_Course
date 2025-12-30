from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, SecretStr

from configs.settings.cors import CorsSettings

SameSite = Literal["lax", "strict", "none"]
JwtAlgorithm = Literal["HS256", "RS256"]


class JwtSettings(BaseModel):
    """
    JWT policy:
    - HS256: dùng secret key (internal)
    - RS256: dùng private/public key (SSO/microservices)
    """
    model_config = ConfigDict(frozen=True)

    algorithm: JwtAlgorithm = Field(default="HS256")
    secret_key: SecretStr = Field(...)
    issuer: str = Field(...)
    audience: str = Field(...)

    access_token_ttl_minutes: int = Field(default=15)


class RefreshSessionSettings(BaseModel):
    """
    Refresh session policy:
    - TTL tính theo minutes (đồng bộ với env)
    - rotate_on_refresh: luôn rotate để chống replay
    """
    model_config = ConfigDict(frozen=True)

    ttl_minutes: int = Field(default=60 * 24 * 14)
    rotate_on_refresh: bool = Field(default=True)


class RefreshCookieSettings(BaseModel):
    """
    Settings cho refresh token cookie:
    - path: đặt ở scope /api hoặc /api/v1/auth (tránh hard-code endpoint cụ thể /refresh)
    - secure=True trong prod (HTTPS)
    - samesite=strict nếu same-site; nếu cross-site SPA thì thường phải cân nhắc none+lax tùy kiến trúc
    """

    model_config = ConfigDict(frozen=True)

    name: str = Field(default="refresh_token")
    path: str = Field(default="/api/v1/auth")  # cookie chỉ gửi cho các route /auth
    secure: bool = Field(default=True)  # secure=true: cookie CHỈ được gửi qua HTTPS
    samesite: SameSite = Field(default="strict")  # dùng để giảm nguy cơ CSRF (Cross-Site Request Forgery)
    max_age_seconds: int = Field(default=60 * 60 * 24 * 14)  # 14 days


class SecuritySettings(BaseModel):
    """
    Nhóm cấu hình security, có thể mở rộng thêm:
    - cookie_domain
    - etc...
    """

    model_config = ConfigDict(frozen=True)

    jwt: JwtSettings  # vì JwtSettings có field required -> được map từ env trong Settings
    refresh_session: RefreshSessionSettings = Field(default_factory=RefreshSessionSettings)
    refresh_cookie: RefreshCookieSettings = Field(default_factory=RefreshCookieSettings)
    cors: CorsSettings = Field(default_factory=CorsSettings)
