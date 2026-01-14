from typing import Any
from models.user import User
from core.utils.json_utils import to_json_safe

# allowlist for User snapshot
USER_AUDIT_FIELDS = (
    "id",
    "email",
    "is_active",
    "token_version",
    # audit mixin
    "is_deleted",
    "deleted_at",
    "deleted_by",
    "created_by",
    "updated_by",
    # time mixin
    "created_at",
    "updated_at",
)

def snapshot_user(user: User) -> dict[str, Any]:
    data: dict[str, Any] = {}

    for f in USER_AUDIT_FIELDS:
        if hasattr(user, f):
            data[f] = to_json_safe(getattr(user, f))

    # normalize id to str
    if "id" in data and data["id"] is not None:
        data["id"] = str(data["id"])

    # MUST NOT include hashed_password (deny by design: allowlist)
    return data
