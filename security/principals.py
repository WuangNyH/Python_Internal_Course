import uuid
from typing import Any
from pydantic import BaseModel, Field, ConfigDict

from security.jwt_claims import JwtClaims


class CurrentUser(BaseModel):
    model_config = ConfigDict(frozen=True) # CurrentUser nên là immutable

    user_id: uuid.UUID
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

        sub = claims.get(JwtClaims.SUBJECT)
        tv = claims.get(JwtClaims.TOKEN_VERSION, 1)
        tid = claims.get(JwtClaims.TENANT_ID)

        if not sub:
            raise ValueError(">>>>> Missing subject (sub) in token claims")

        try:
            user_uuid = uuid.UUID(str(sub))
        except (ValueError, TypeError):
            raise ValueError(">>>>> Invalid subject (sub) ID")

        # cls(...): gọi __init__ để khởi tạo đối tượng CurrentUser
        return cls(
            user_id=user_uuid,

            # always empty for access token
            roles=[],
            permissions=set(),

            token_version=int(tv),
            tenant_id=tid,
        )
