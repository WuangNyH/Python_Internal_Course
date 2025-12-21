from typing import Literal

from fastapi import Response

SameSite = Literal["lax", "strict", "none"]


class RefreshCookiePolicy:
    def __init__(
            self,
            *,
            name: str = "refresh_token",
            path: str = "/api/v1/auth/refresh",
            secure: bool = True,
            samesite: SameSite = "strict",
            max_age_seconds: int = 60 * 60 * 24 * 14,
    ):
        self.name = name
        self.path = path
        self.secure = secure
        self.samesite: SameSite = samesite
        self.max_age_seconds = max_age_seconds

    def set(self, response: Response, token: str) -> None:
        response.set_cookie(
            key=self.name,
            value=token,
            httponly=True,
            secure=self.secure,
            samesite=self.samesite,
            max_age=self.max_age_seconds,
            path=self.path,
        )

    def clear(self, response: Response) -> None:
        response.delete_cookie(key=self.name, path=self.path)
