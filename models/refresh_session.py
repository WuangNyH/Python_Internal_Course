import uuid
from datetime import datetime

from sqlalchemy import (
    ForeignKey,
    String,
    DateTime,
    Index,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base
from models.time_mixin import TimeMixin


class RefreshSession(TimeMixin, Base):
    __tablename__ = "refresh_sessions"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # ---- Token storage (hash only) ----
    token_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,
        comment="Hashed refresh token (never store plain token)",
    )

    # ---- Lifecycle ----
    # Nếu user không refresh trong expires_at phút -> hết session -> login lại
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    # Dù refresh liên tục, sau absolute_expires_at ngày kể từ login -> hết session
    absolute_expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    revoked_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    rotated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # ---- Metadata (tùy dự án) ----
    # Quản lý đa thiết bị / đa phiên đăng nhập (Chrome / Windows ...)
    user_agent: Mapped[str | None] = mapped_column(String(255), nullable=True)
    ip_address: Mapped[str | None] = mapped_column(String(45), nullable=True)

    # ---- Relationship ----
    user = relationship("User", lazy="selectin")

    __table_args__ = (
        UniqueConstraint("token_hash", name="uq_refresh_sessions_token_hash"),
        Index("ix_refresh_sessions_user_active", "user_id", "revoked_at"),
    )
