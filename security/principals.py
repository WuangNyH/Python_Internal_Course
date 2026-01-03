from typing import Any
from pydantic import BaseModel, Field, ConfigDict


class CurrentUser(BaseModel):
    model_config = ConfigDict(frozen=True) # CurrentUser nên là immutable

    user_id: int
    roles: list[str] = Field(default_factory=list)
    permissions: set[str] = Field(default_factory=set)

    token_version: int = 1
    tenant_id: str | None = None

    # factory method (tạo ra một CurrentUser):
    # - nhận: raw claims data
    # - nhiệm vụ: map field, set default, normalize
    # - trả: domain object (CurrentUser)
    @classmethod # Tại thời điểm gọi chưa
    def from_claims(cls, claims: dict[str, Any]) -> CurrentUser:
        # cls là param đặc biệt khi dùng chung với @classmethod
        # cls là tham chiếu tới class đang gọi method (ở đây là CurrentUser)

        sub = claims.get("sub")
        roles = claims.get("roles") or []
        perms = claims.get("permissions") or []
        tv = claims.get("tv") or claims.get("token_version") or 1

        # cls(...): gọi __init__ để khởi tạo đối tượng CurrentUser
        return cls(
            user_id=int(sub), # sub thường là string -> cần convert int
            roles=list(roles),
            permissions=set(perms),
            token_version=int(tv),
            tenant_id=claims.get("tid"),
        )
