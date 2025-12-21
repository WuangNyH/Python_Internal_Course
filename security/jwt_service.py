from datetime import datetime, timedelta, timezone
from typing import Any

from jose import jwt
from jose.exceptions import ExpiredSignatureError, JWTError

from configs.env import settings_config

_settings = settings_config()

JWT_ALGORITHM = _settings.jwt_algorithm
JWT_SECRET_KEY = _settings.jwt_secret_key
JWT_ISSUER = _settings.jwt_issuer
JWT_AUDIENCE = _settings.jwt_audience


def create_access_token(
    *,
    subject: str,
    permissions: list[str],
    roles: list[str] | None = None,
    expires_minutes: int = 15,
    extra_claims: dict[str, Any] | None = None,
) -> str:
    now = datetime.now(timezone.utc)
    payload: dict[str, Any] = {
        "sub": subject,
        "iss": JWT_ISSUER,
        "aud": JWT_AUDIENCE,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=expires_minutes)).timestamp()),
        "permissions": permissions,
        "roles": roles or [],
    }
    if extra_claims:
        payload.update(extra_claims)

    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


def decode_access_token(token: str) -> tuple[dict[str, Any] | None, str | None]:
    try:
        claims = jwt.decode(
            token,
            JWT_SECRET_KEY,
            algorithms=[JWT_ALGORITHM],
            audience=JWT_AUDIENCE,
            issuer=JWT_ISSUER,
            options={"require_aud": True, "require_iss": True},
        )
        return claims, None
    except ExpiredSignatureError:
        return None, "expired"
    except JWTError:
        return None, "invalid"
