from datetime import datetime, timedelta, timezone
from typing import Any
from jose import jwt
from jose.exceptions import ExpiredSignatureError, JWTError

from configs.settings.security import JwtSettings
from security.jwt_claims import JwtClaims
from core.security.types import TokenError


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
            JwtClaims.SUBJECT: subject,
            JwtClaims.ISSUER: self._settings.issuer,
            JwtClaims.AUDIENCE: self._settings.audience,
            JwtClaims.ISSUED_AT: int(now.timestamp()),
            JwtClaims.EXPIRES_AT: int((now + timedelta(
                minutes=self._settings.access_token_ttl_minutes)).timestamp()),
            JwtClaims.TOKEN_VERSION: token_version,
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
            return None, TokenError.EXPIRED
        except JWTError:
            return None, TokenError.INVALID
