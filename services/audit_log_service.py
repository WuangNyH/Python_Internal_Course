import uuid
from typing import Any, Mapping

from sqlalchemy.orm import Session

from core.audit.audit_actions import AuditAction
from core.audit.audit_mode import AuditMode
from core.utils.json_utils import to_json_safe
from models.audit_log import AuditLog
from repositories.audit_log_repository import AuditLogRepository
from schemas.request.audit_log_schema import AuditLogSearchParams
from schemas.response.audit_log_out_schema import AuditLogOut, AuditLogListOut
from security.sensitive_fields import SENSITIVE_FIELDS, MASK_ALL


class AuditLogService:
    """
    Enterprise audit log service (append-only).

    Responsibilities:
    - Create audit events (sanitize before/after payload to avoid sensitive data leaks)
    - Search events and map ORM -> AuditLogOut
    """

    # Actions considered security-critical
    _SECURITY_ONLY_ACTIONS: frozenset[AuditAction] = frozenset(
        {
            # Auth
            AuditAction.AUTH_LOGIN_SUCCESS,
            AuditAction.AUTH_LOGIN_FAILED,
            AuditAction.AUTH_LOGOUT,
            AuditAction.AUTH_REFRESH_FAILED,
            AuditAction.AUTH_REVOKE_ALL_SESSIONS,
            # NOTE: "Ko log refresh success" => do not include AUTH_ROTATE_REFRESH

            # User security state
            AuditAction.USER_ACTIVATE,
            AuditAction.USER_DEACTIVATE,
            AuditAction.USER_DELETE,

            # Authz changes
            AuditAction.ROLE_ASSIGN,
            AuditAction.ROLE_REVOKE,
            AuditAction.PERMISSION_GRANT,
            AuditAction.PERMISSION_REVOKE,

            # System
            AuditAction.SYSTEM_JOB,
        }
    )

    def __init__(
            self,
            audit_log_repo: AuditLogRepository | None = None,
            *,
            audit_mode: AuditMode = AuditMode.ON,
    ):
        self.repo = audit_log_repo or AuditLogRepository()
        self.audit_mode = audit_mode

    # ======= Write (append-only) =======
    def log_event(
            self,
            db: Session,
            *,
            action: AuditAction,
            entity_type: str,
            entity_id: str,
            actor_user_id: uuid.UUID | None = None,
            request_id: str | None = None,
            trace_id: str | None = None,
            ip: str | None = None,
            user_agent: str | None = None,
            before: Mapping[str, Any] | None = None,
            after: Mapping[str, Any] | None = None,
            message: str | None = None,
    ) -> AuditLog | None:
        """
        Create an audit log event row (append-only).
        - Does NOT commit. Transaction handled by middleware.

        Notes:
        - before/after are sanitized + normalized to JSON-safe structures.
        """
        if not self._should_log(action):
            return None

        event = AuditLog(
            actor_user_id=actor_user_id,
            action=action.value.strip(),
            entity_type=str(entity_type).strip(),
            entity_id=str(entity_id).strip(),
            request_id=(str(request_id).strip() if request_id else None),
            trace_id=(str(trace_id).strip() if trace_id else None),
            ip=ip,
            user_agent=user_agent,
            before=self._sanitize_payload(before) if before is not None else None,
            after=self._sanitize_payload(after) if after is not None else None,
            message=(str(message) if message else None),
        )

        # append-only insert
        return self.repo.create_event(db, event=event)

    # Convenience helper when having ORM entity objects
    def log_entity_event(
            self,
            db: Session,
            *,
            action: AuditAction,
            entity: Any,
            actor_user_id: uuid.UUID | None = None,
            request_id: str | None = None,
            trace_id: str | None = None,
            ip: str | None = None,
            user_agent: str | None = None,
            before: Mapping[str, Any] | None = None,
            after: Mapping[str, Any] | None = None,
            message: str | None = None,
            entity_type: str | None = None,
            entity_id: str | None = None,
    ) -> AuditLog | None:
        """
        Log using an ORM entity as target.
        - entity_type defaults to entity.__class__.__name__
        - entity_id defaults to str(entity.id) if exists
        """
        resolved_entity_type = entity_type or getattr(entity, "__class__", type("X", (), {})).__name__
        resolved_entity_id = entity_id
        if resolved_entity_id is None:
            eid = getattr(entity, "id", None)
            resolved_entity_id = str(eid) if eid is not None else "unknown"

        return self.log_event(
            db,
            action=action,
            entity_type=resolved_entity_type,
            entity_id=resolved_entity_id,
            actor_user_id=actor_user_id,
            request_id=request_id,
            trace_id=trace_id,
            ip=ip,
            user_agent=user_agent,
            before=before,
            after=after,
            message=message,
        )

    # ======= Read =======
    def search(
            self,
            db: Session,
            *,
            params: AuditLogSearchParams,
    ) -> AuditLogListOut:
        """
        Search audit logs by AuditLogSearchParams and return response DTO
        """
        items, total, meta = self.repo.search(db, params=params)

        return AuditLogListOut(
            items=[AuditLogOut.model_validate(x) for x in items],
            total=total,
            page=meta.page,
            page_size=meta.page_size,
        )

    # ======= Internal helpers =======
    def _should_log(self, action: AuditAction) -> bool:
        if self.audit_mode == AuditMode.OFF:
            return False
        if self.audit_mode == AuditMode.SECURITY_ONLY:
            return action in self._SECURITY_ONLY_ACTIONS
        return True

    def _sanitize_payload(
            self, payload: Mapping[str, Any] | None
    ) -> dict[str, Any] | None:
        """
        - Remove sensitive keys (denylist)
        - Convert values to JSON-safe primitives
        """
        if payload is None:
            return None

        sanitized: dict[str, Any] = {}
        for k, v in payload.items():
            key = str(k)
            if key in SENSITIVE_FIELDS:
                sanitized[key] = MASK_ALL
            else:
                sanitized[key] = to_json_safe(v)

        return sanitized
