import uuid
from typing import Any

from sqlalchemy.orm import Session

from core.audit.audit_actions import AuditAction
from core.audit.diff.user_audit_diff import diff_user_for_audit
from core.audit.snapshots.user_snapshot import snapshot_user
from core.context.request_context import RequestContext
from models.user import User
from repositories.refresh_session_repository import RefreshSessionRepository
from repositories.user_repository import UserRepository
from schemas.request.user_schema import UserCreate, UserUpdate, UserSearchParams
from core.exceptions.user_exception import (
    UserNotFoundException,
    UserEmailAlreadyExistsException,
    UserDeleteSelfForbiddenException,
    UserUpdateSelfForbiddenException,
)
from security.password import hash_password
from services.audit_log_service import AuditLogService


class UserService:

    def __init__(
            self,
            user_repo: UserRepository | None = None,
            refresh_session_repo: RefreshSessionRepository | None = None,
            audit_log_service: AuditLogService | None = None,
    ):
        self.user_repo = user_repo or UserRepository()
        self.refresh_session_repo = refresh_session_repo or RefreshSessionRepository()
        self.audit_log_service = audit_log_service or AuditLogService()

    # ========= CREATE =========
    def create_user(
            self, db: Session, *, data: UserCreate, ctx: RequestContext,
    ) -> User:
        email = str(data.email).strip().lower()
        existing = self.user_repo.get_by_email(db, email=email)
        if existing is not None:
            raise UserEmailAlreadyExistsException(email=email)

        password_hash = hash_password(data.password)
        actor_user_id = self._actor_user_id(ctx)

        user = User(
            email=email,
            hashed_password=password_hash,
            is_active=bool(getattr(data, "is_active", True)),
            created_by=actor_user_id,
            updated_by=actor_user_id,
        )

        created = self.user_repo.create(db, user)

        # Audit log (append-only)
        self.audit_log_service.log_entity_event(
            db,
            action=AuditAction.USER_CREATE,
            entity=created,
            actor_user_id=actor_user_id,
            request_id=getattr(ctx, "request_id", None),
            trace_id=getattr(ctx, "trace_id", None),
            ip=getattr(ctx, "ip", None),
            user_agent=getattr(ctx, "user_agent", None),
            before=None,
            after=snapshot_user(created),
        )

        return created

    # ========= READ =========
    def get_user_or_404(self, db: Session, *, user_id: uuid.UUID) -> User:
        user = self.user_repo.get_alive_by_id(db, user_id)
        if not user:
            raise UserNotFoundException(user_id=user_id)
        return user

    def get_user_by_email(self, db: Session, *, email: str) -> User:
        user = self.user_repo.get_by_email(db, email=str(email).strip().lower())
        if not user:
            raise UserNotFoundException()
        return user

    def search_users(
            self, db: Session, *, params: UserSearchParams
    ) -> tuple[list[User], int, Any]:
        """
        Search for users in the database based on the given search parameters.

        This method interacts with the repository layer to perform user search operations.
        It returns a tuple containing the list of users matching the search criteria, the
        total count of matching users, and an optional third value (could represent additional
        metadata or information).

        :param db: The SQLAlchemy Session object used to interface with the database.
        :param params: An instance of UserSearchParams containing the criteria for searching
            users in the database.
        :return: A tuple consisting of:
            - A list of User objects matching the search criteria.
            - An integer representing the total number of matching user records.
            - An optional value providing additional metadata or information related to
              the search result.
        """
        return self.user_repo.search(db, params=params)

    def list_users(
            self, db: Session, *, offset: int = 0, limit: int = 100
    ) -> list[User]:
        return list(self.user_repo.list_active(db, offset=offset, limit=limit))

    # ========= UPDATE =========
    def update_user(
            self,
            db: Session,
            *,
            user_id: uuid.UUID,
            data: UserUpdate,
            ctx: RequestContext,
            forbid_self_update: bool = False,
    ) -> User:
        actor_user_id = self._actor_user_id(ctx)

        self._ensure_can_update_target(
            actor_user_id=actor_user_id,
            target_user_id=user_id,
            forbid_self_update=forbid_self_update,
        )

        user = self.get_user_or_404(db, user_id=user_id)

        before = snapshot_user(user)
        update_data = data.model_dump(exclude_unset=True)

        # ----- Apply updates -----
        self._apply_email_update(
            db, user_id=user_id, user=user, update_data=update_data,
        )

        # Track status change for better audit action
        before_is_active = bool(getattr(user, "is_active", False))
        new_is_active = update_data.get("is_active", None)
        deactivated = (new_is_active is False) and before_is_active
        is_active_changed = False
        if "is_active" in update_data and new_is_active is not None:
            after_is_active = bool(update_data["is_active"])
            is_active_changed = (after_is_active != before_is_active)

        # If password change -> password_hash
        password_changed = self._apply_password_update(update_data=update_data)

        # Bump token_version + revoke all refresh sessions:
        # - active -> inactive
        # - password change
        if password_changed or deactivated:
            self._force_logout_all(db, user=user, update_data=update_data)

        # Audit columns
        update_data["updated_by"] = actor_user_id

        updated = self.user_repo.update(db, user, update_data)
        after = snapshot_user(updated)

        diff = diff_user_for_audit(
            before=before,
            after=after,
            password_changed=password_changed,
            include_changes=True,
        )

        # Merge changed_fields (+ changes) into after payload
        audit_after: dict[str, Any] = {**after, **diff.after_patch}

        # Choose action USER_ACTIVATE/USER_DEACTIVATE if updated is_active
        action = AuditAction.USER_UPDATE
        if is_active_changed:
            action = AuditAction.USER_ACTIVATE if bool(
                getattr(updated, "is_active", False)
            ) else AuditAction.USER_DEACTIVATE

        self.audit_log_service.log_entity_event(
            db,
            action=action,
            entity=updated,
            actor_user_id=actor_user_id,
            request_id=getattr(ctx, "request_id", None),
            trace_id=getattr(ctx, "trace_id", None),
            ip=getattr(ctx, "ip", None),
            user_agent=getattr(ctx, "user_agent", None),
            before=before,
            after=audit_after,
        )

        return updated

    # ========= DELETE =========
    def delete_user(
            self,
            db: Session,
            *,
            user_id: uuid.UUID,
            ctx: RequestContext,
            hard_delete: bool = False,
    ) -> None:
        actor_user_id = self._actor_user_id(ctx)

        # Forbid deleting self
        if actor_user_id is not None and actor_user_id == user_id:
            raise UserDeleteSelfForbiddenException(user_id=user_id)

        user = self.get_user_or_404(db, user_id=user_id)
        before = snapshot_user(user)

        self._revoke_all_refresh_sessions(db, user_id=user.id)

        if hard_delete:
            self.user_repo.delete(db, user)
            message = "hard_delete"
            after = None  # hard delete -> no after state
        else:
            # Bump token_version
            user.token_version = int(getattr(user, "token_version", 1)) + 1

            self.user_repo.soft_delete(db, user, actor_user_id=actor_user_id)
            message = "soft_delete"
            db.refresh(user)
            after = snapshot_user(user)

        self.audit_log_service.log_entity_event(
            db,
            action=AuditAction.USER_DELETE,
            entity=user,
            actor_user_id=actor_user_id,
            request_id=getattr(ctx, "request_id", None),
            trace_id=getattr(ctx, "trace_id", None),
            ip=getattr(ctx, "ip", None),
            user_agent=getattr(ctx, "user_agent", None),
            before=before,
            after=after,
            message=message,
        )

    # ===== Private helpers =====

    @staticmethod
    def _ensure_can_update_target(
            *,
            actor_user_id: uuid.UUID | None,
            target_user_id: uuid.UUID,
            forbid_self_update: bool,
    ) -> None:
        if not forbid_self_update:
            return
        if actor_user_id is None:
            return

        # Optional rule: forbid self update
        if actor_user_id == target_user_id:
            raise UserUpdateSelfForbiddenException(user_id=target_user_id)

    @staticmethod
    def _bump_token_version(
            *, user: User, update_data: dict[str, Any]) -> None:
        # revoke existing tokens by bumping token_version
        current = getattr(user, "token_version", 0)
        try:
            update_data["token_version"] = int(current or 0) + 1
        except (TypeError, ValueError):
            update_data["token_version"] = 1

    def _actor_user_id(self, ctx: RequestContext) -> uuid.UUID | None:
        return ctx.current_user.user_id if ctx.current_user else None

    def _apply_email_update(
            self,
            db: Session,
            *,
            user_id: uuid.UUID,
            user: User,
            update_data: dict[str, Any],
    ) -> None:
        if "email" not in update_data:
            return

        raw = update_data.get("email")
        if raw is None:
            # client explicitly sets null -> ignore for email
            update_data.pop("email", None)
            return

        new_email = str(raw).strip().lower()
        if new_email == user.email:
            update_data.pop("email", None)
            return

        existing = self.user_repo.get_by_email(db, email=new_email)
        if existing is not None and getattr(existing, "id", None) != user_id:
            raise UserEmailAlreadyExistsException(email=new_email)

        update_data["email"] = new_email

    def _apply_password_update(
            self,
            *,
            update_data: dict[str, Any],
    ) -> bool:
        if "password" not in update_data:
            return False

        new_password = update_data.pop("password", None)
        if new_password is None:
            return False

        if not isinstance(new_password, str):
            raise TypeError("password must be a string")

        hashed = hash_password(new_password)
        if not hashed:
            raise RuntimeError("Password hashing failed")

        update_data["hashed_password"] = hashed
        return True

    def _revoke_all_refresh_sessions(self, db: Session, *, user_id: uuid.UUID) -> int:
        return self.refresh_session_repo.revoke_all_for_user(db=db, user_id=user_id)

    def _force_logout_all(
            self, db: Session, *, user: User, update_data: dict[str, Any]
    ) -> None:
        self._bump_token_version(user=user, update_data=update_data)
        self._revoke_all_refresh_sessions(db, user_id=user.id)
