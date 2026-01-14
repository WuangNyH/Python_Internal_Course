import uuid
from sqlalchemy import Boolean, Column, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql.base import UUID
from sqlalchemy.sql import func

USER_ID_FK = "users.id"


class AuditMixin:
    created_by = Column(UUID(as_uuid=True), ForeignKey(USER_ID_FK), nullable=True, index=True)
    updated_by = Column(UUID(as_uuid=True), ForeignKey(USER_ID_FK), nullable=True, index=True)

    is_deleted = Column(Boolean, nullable=False, server_default="false", index=True)
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    deleted_by = Column(UUID(as_uuid=True), ForeignKey(USER_ID_FK), nullable=True, index=True)

    def mark_deleted(self, *, actor_user_id: uuid.UUID | None) -> None:
        self.is_deleted = True
        self.deleted_at = func.now()  # DB time
        self.deleted_by = actor_user_id
