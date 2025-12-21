from __future__ import annotations

from typing import Any
from pydantic import BaseModel, Field, ConfigDict


class CurrentUser(BaseModel):
    model_config = ConfigDict(frozen=True)

    user_id: int
    roles: list[str] = Field(default_factory=list)
    permissions: set[str] = Field(default_factory=set)

    token_version: int = 1
    tenant_id: str | None = None

    @classmethod
    def from_claims(cls, claims: dict[str, Any]) -> "CurrentUser":
        # sub thường là string -> convert
        sub = claims.get("sub")
        roles = claims.get("roles") or []
        perms = claims.get("permissions") or []
        tv = claims.get("tv") or claims.get("token_version") or 1

        return cls(
            user_id=int(sub),
            roles=list(roles),
            permissions=set(perms),
            token_version=int(tv),
            tenant_id=claims.get("tid"),
        )
