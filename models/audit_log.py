import uuid

from sqlalchemy import (
    BigInteger,
    DateTime,
    ForeignKey,
    Index,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

from models.base import Base


class AuditLog(Base):
    """
    Enterprise audit log (append-only).

    Captures:
    - actor_user_id (who)
    - action (what)
    - entity_type/entity_id (target)
    - request_id/trace_id (correlation)
    - ip/user_agent (origin)
    - before/after payload (diff context)
    """

    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    # Timestamp of the event (append-only, never updated)
    created_at: Mapped[object] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        index=True,
    )

    # Who performed the action (nullable for system/background jobs)
    actor_user_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=True,
        index=True,
    )

    # What action happened: "USER_CREATE", "USER_UPDATE", "USER_DELETE", "AUTH_LOGIN", ...
    action: Mapped[str] = mapped_column(String(64), nullable=False, index=True)

    # Target entity
    entity_type: Mapped[str] = mapped_column(String(64), nullable=False, index=True)  # e.g. "User"
    entity_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)  # store as string for generic use

    # Request correlation
    request_id: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    trace_id: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)

    # Client metadata (optional)
    ip: Mapped[str | None] = mapped_column(String(64), nullable=True)
    user_agent: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Payload snapshots (optional)
    # Prefer JSONB for Postgres (fast query / indexing if needed)
    before: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    after: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    # Optional free-form message / reason (e.g. "token_revoked", "admin_action", ...)
    message: Mapped[str | None] = mapped_column(Text, nullable=True)


# Composite indexes for common audit queries
Index("ix_audit_logs_entity", AuditLog.entity_type, AuditLog.entity_id, AuditLog.created_at)
Index("ix_audit_logs_actor_time", AuditLog.actor_user_id, AuditLog.created_at)
