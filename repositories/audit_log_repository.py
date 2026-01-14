from typing import Any
from sqlalchemy import select
from sqlalchemy.orm import Session

from core.http.pagination import PageMeta, PageParams
from core.http.sorting import SortSpec, parse_sort
from models.audit_log import AuditLog
from repositories.base_repository import BaseRepository
from schemas.request.audit_log_schema import AuditLogSearchParams


class AuditLogRepository(BaseRepository[AuditLog]):
    """
    Enterprise audit log repository (append-only).

    - create_event(): insert new audit event
    - search(): query audit events by AuditLogSearchParams (filters + paging + sort)
    """

    _SORT_FIELDS: dict[str, Any] = {
        "id": AuditLog.id,
        "created_at": AuditLog.created_at,
        "action": AuditLog.action,
        "entity_type": AuditLog.entity_type,
        "entity_id": AuditLog.entity_id,
        "actor_user_id": AuditLog.actor_user_id,
        "request_id": AuditLog.request_id,
        "trace_id": AuditLog.trace_id,
    }

    def __init__(self):
        super().__init__(AuditLog)

    # ===== WRITE (append-only) =====
    def create_event(self, db: Session, *, event: AuditLog) -> AuditLog:
        return self.create(db, event)

    # ===== READ =====
    def search(self, db: Session, *, params: AuditLogSearchParams) -> tuple[list[AuditLog], int, PageMeta]:
        """
        Search audit logs by AuditLogSearchParams.

        :return: tuple[items, total, meta]
        """
        stmt = select(AuditLog)
        stmt = self._apply_filters(stmt, params=params)

        total = self.count(db, stmt)

        page_params = PageParams(page=params.page, page_size=params.page_size)

        sort_specs: list[SortSpec] | None = None
        if params.sort:
            # params.sort has been strictly validated by StrictSortParams
            sort_specs = parse_sort(params.sort)

        return self._execute_search(
            db=db,
            stmt=stmt,
            total=total,
            page=page_params,
            sort_specs=sort_specs,
            allowed_sort_fields=self._SORT_FIELDS,
            default_sorts=[SortSpec(field="created_at", direction="desc")],
        )

    # ===== Internal helpers =====
    def _apply_filters(self, stmt, *, params: AuditLogSearchParams):
        if params.actor_user_id is not None:
            stmt = stmt.where(AuditLog.actor_user_id == params.actor_user_id)

        if params.action:
            stmt = stmt.where(AuditLog.action == params.action)

        if params.entity_type:
            stmt = stmt.where(AuditLog.entity_type == params.entity_type)

        if params.entity_id:
            stmt = stmt.where(AuditLog.entity_id == params.entity_id)

        if params.request_id:
            stmt = stmt.where(AuditLog.request_id == params.request_id)

        if params.trace_id:
            stmt = stmt.where(AuditLog.trace_id == params.trace_id)

        if params.created_from:
            stmt = stmt.where(AuditLog.created_at >= params.created_from)

        if params.created_to:
            stmt = stmt.where(AuditLog.created_at <= params.created_to)

        return stmt
