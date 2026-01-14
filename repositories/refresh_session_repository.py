import uuid
from datetime import datetime
from typing import Final

from sqlalchemy import delete, select, or_
from sqlalchemy.orm import Session

from core.utils.datetime_utils import utcnow
from models.refresh_session import RefreshSession


class RefreshSessionRepository:
    MODEL: Final = RefreshSession

    # Create / Issue
    def create_session(
            self,
            db: Session,
            *,
            user_id: uuid.UUID,
            token_hash: str,
            expires_at: datetime,
            absolute_expires_at: datetime,
            user_agent: str | None = None,
            ip_address: str | None = None,
            now: datetime | None = None,
    ) -> RefreshSession:
        now = now or utcnow()

        session = RefreshSession(
            user_id=user_id,
            token_hash=token_hash,
            expires_at=expires_at,
            absolute_expires_at=absolute_expires_at,
            user_agent=user_agent,
            ip_address=ip_address,
            created_at=now,
            updated_at=now,
        )
        db.add(session)
        db.flush()  # lấy session.id ngay trong transaction
        return session

    # Read / Validate
    def get_active_by_token_hash(
            self,
            db: Session,
            *,
            token_hash: str,
            now: datetime | None = None,
            for_update: bool = False,
    ) -> RefreshSession | None:
        """
        Lấy refresh session còn hiệu lực:
        - token_hash match
        - revoked_at is NULL
        - expires_at > now

        for_update=True dùng cho flow refresh/rotate để tránh race-condition
        """
        now = now or utcnow()

        stmt = (
            select(RefreshSession)
            .where(
                RefreshSession.token_hash == token_hash,
                RefreshSession.revoked_at.is_(None),
                RefreshSession.expires_at > now,
                RefreshSession.absolute_expires_at > now,
            )
        )

        if for_update:
            stmt = stmt.with_for_update(of=RefreshSession)

        return db.execute(stmt).scalars().first()

    # Rotate
    def rotate_session(
            self,
            db: Session,
            *,
            old_token_hash: str,
            new_token_hash: str,
            new_expires_at: datetime,
            now: datetime | None = None,
    ) -> RefreshSession | None:
        """
        Rotate refresh token theo pattern enterprise:
        - Lock row theo old_token_hash (FOR UPDATE) để tránh concurrent refresh
        - Nếu session không còn active -> return None
        - Update token_hash + expires_at + rotated_at + updated_at

        Lưu ý: rotate theo kiểu "update-in-place" (1 row)
        Do token_hash unique, new_token_hash phải chưa tồn tại
        """
        now = now or utcnow()

        # Lock & validate session
        current = self.get_active_by_token_hash(
            db,
            token_hash=old_token_hash,
            now=now,
            for_update=True,
        )
        if not current:
            return None

        # Update tại chỗ
        current.token_hash = new_token_hash
        current.rotated_at = now
        current.updated_at = now
        # Gia hạn expires_at nhưng KHÔNG vượt quá absolute_expires_at
        current.expires_at = min(new_expires_at, current.absolute_expires_at)

        db.flush()
        return current

    # Revoke
    def revoke_by_token_hash(
            self,
            db: Session,
            *,
            token_hash: str,
            now: datetime | None = None,
    ) -> bool:
        """
        Revoke 1 session theo token_hash
        """
        now = now or utcnow()

        session = self.get_active_by_token_hash(
            db,
            token_hash=token_hash,
            now=now,
            for_update=True,
        )
        if not session:
            return False

        session.revoked_at = now
        session.updated_at = now
        db.flush()
        return True

    def revoke_all_for_user(
            self,
            db: Session,
            *,
            user_id: uuid.UUID,
            now: datetime | None = None,
    ) -> int:
        """
        Revoke tất cả session của 1 user (logout all devices)
        Return: số session bị revoke
        """
        now = now or utcnow()

        stmt = (
            select(RefreshSession)
            .where(
                RefreshSession.user_id == user_id,
                RefreshSession.revoked_at.is_(None),
            )
            .with_for_update()
        )

        sessions = db.execute(stmt).scalars().all()
        if not sessions:
            return 0

        for s in sessions:
            s.revoked_at = now
            s.updated_at = now

        db.flush()
        return len(sessions)

    # Cleanup
    def delete_expired_sessions(
            self,
            db: Session,
            *,
            before: datetime | None = None,
    ) -> int:
        """
        Dọn dẹp session hết hạn (enterprise chạy cron/job)
        Return: số session bị xóa
        """
        before = before or utcnow()

        # Lấy danh sách id cần xóa
        id_stmt = select(RefreshSession.id).where(
            or_(
                RefreshSession.expires_at <= before,
                RefreshSession.absolute_expires_at <= before
            )
        )
        ids = db.execute(id_stmt).scalars().all()
        if not ids:
            return 0

        # Xóa theo ids (an toàn, không phụ thuộc rowcount)
        del_stmt = delete(RefreshSession).where(RefreshSession.id.in_(ids))
        db.execute(del_stmt)

        return len(ids)
