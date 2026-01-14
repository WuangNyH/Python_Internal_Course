import uuid
from typing import Any, ClassVar
from pydantic import Field, field_validator

from schemas.request.search_common import PagedSortParams, CreatedRangeParams, StrictSortParams


class AuditLogSearchParams(PagedSortParams, StrictSortParams, CreatedRangeParams):
    """
    Search params for audit logs.
    Mirrors AuditLogRepository.search() filters + paging/sort.
    """

    MAX_PAGE_SIZE: ClassVar[int] = 100
    ALLOWED_SORT_FIELDS: ClassVar[set[str]] = {
        "id",
        "created_at",
        "action",
        "entity_type",
        "entity_id",
        "actor_user_id",
        "request_id",
        "trace_id",
    }

    # ---- Filters ----
    actor_user_id: uuid.UUID | None = Field(default=None, description="Filter by actor user id")
    action: str | None = Field(default=None, description="Exact match audit action, e.g. USER_UPDATE")
    entity_type: str | None = Field(default=None, description='Exact match entity type, e.g. "User"')
    entity_id: str | None = Field(default=None, description="Exact match entity id (stored as string)")
    request_id: str | None = Field(default=None, description="Filter by request_id")
    trace_id: str | None = Field(default=None, description="Filter by trace_id")

    @field_validator(
        "action",
        "entity_type",
        "entity_id",
        "request_id",
        "trace_id",
        mode="before",
    )
    @classmethod
    def normalize_str(cls, v: Any) -> str | None:
        if v is None:
            return None
        s = str(v).strip()
        return s or None
