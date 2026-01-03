from fastapi import Response

from configs.settings.security import RefreshCookieSettings


class RefreshCookiePolicy:
    def __init__(self, settings: RefreshCookieSettings):
        self._settings = settings

    @property
    def name(self) -> str:
        return self._settings.name

    @property
    def path(self) -> str:
        return self._settings.path

    def set(self, response: Response, token: str) -> None:
        response.set_cookie(
            key=self._settings.name,
            value=token,
            httponly=True, # chặn ko cho JavaScript đọc cookie => ngăn tấn công XSS
            secure=self._settings.secure,
            samesite=self._settings.samesite,
            max_age=self._settings.max_age_seconds,
            path=self._settings.path,
        )

    def clear(self, response: Response) -> None:
        response.delete_cookie(key=self._settings.name, path=self._settings.path)
