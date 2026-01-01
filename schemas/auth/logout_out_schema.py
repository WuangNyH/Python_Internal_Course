from pydantic import BaseModel


class LogoutAllResult(BaseModel):
    revoked_sessions: int