from datetime import datetime, timedelta, timezone
from typing import Any

from jose import jwt
from jose.exceptions import ExpiredSignatureError, JWTError

from configs.settings.security import JwtSettings


class JwtService:
    def __init__(self, settings: JwtSettings):
        self._settings = settings

    def create_access_token(
        self,
        *,
        subject: str,
        token_version: int = 1,
        extra_claims: dict[str, Any] | None = None,
    ) -> str:
        now = datetime.now(timezone.utc)

        payload: dict[str, Any] = {
            "sub": subject,
            "iss": self._settings.issuer,
            "aud": self._settings.audience,
            "iat": now,
            "exp": now + timedelta(minutes=self._settings.access_token_ttl_minutes),
            "tv": token_version,
        }
        if extra_claims:
            payload.update(extra_claims)

        return jwt.encode(
            payload,
            self._settings.secret_key.get_secret_value(),
            algorithm=self._settings.algorithm,
        )

    def decode_access_token(self, token: str) -> tuple[dict[str, Any] | None, str | None]:
        try:
            claims = jwt.decode(
                token,
                self._settings.secret_key.get_secret_value(),
                algorithms=[self._settings.algorithm],
                audience=self._settings.audience,
                issuer=self._settings.issuer,
                options={
                    "require_aud": True,
                    "require_iss": True,
                },
            )
            return claims, None
        except ExpiredSignatureError:
            return None, "expired"
        except JWTError:
            return None, "invalid"
