import uuid
from typing import TYPE_CHECKING
from sqlalchemy import String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.audit_mixin import AuditMixin
from models.base import Base
from models.associations import user_roles
from models.time_mixin import TimeMixin

if TYPE_CHECKING:
    from models.role import Role


class User(TimeMixin, AuditMixin, Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(nullable=False)
    is_active: Mapped[bool] = mapped_column(nullable=False, default=False)
    token_version: Mapped[int] = mapped_column(nullable=False, default=1)

    roles: Mapped[list[Role]] = relationship(
        "Role",
        secondary=user_roles,
        back_populates="users",
        lazy="selectin",
    )
