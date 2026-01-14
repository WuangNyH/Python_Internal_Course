import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class AuditLogOut(BaseModel):
    """
    Response DTO for audit logs.

    Notes:
    - model_config(from_attributes=True) để map trực tiếp từ SQLAlchemy ORM object
    - before/after dùng dict[str, Any] | None để phản ánh JSONB
    - Audit log là append-only => chỉ có created_at
    """

    model_config = ConfigDict(from_attributes=True, frozen=True)

    id: int
    created_at: datetime

    actor_user_id: uuid.UUID | None = Field(default=None)
    action: str

    entity_type: str
    entity_id: str

    request_id: str | None = None
    trace_id: str | None = None

    ip: str | None = None
    user_agent: str | None = None

    before: dict[str, Any] | None = None
    after: dict[str, Any] | None = None

    message: str | None = None


class AuditLogListOut(BaseModel):
    items: list[AuditLogOut]
    total: int
    page: int
    page_size: int
