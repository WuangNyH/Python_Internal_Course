import uuid
from sqlalchemy.orm import Session, selectinload
from sqlalchemy import select

from models.user import User
from models.role import Role


class AuthRepository:
    def get_user_credentials_by_email(self, db: Session, email: str) -> User | None:
        stmt = select(User).where(User.email == email)
        return db.execute(stmt).scalars().first()

    def get_authz_snapshot(
            self, db: Session, user_id: uuid.UUID
    ) -> tuple[list[str], list[str], int]:
        """
        Load user + authz relations, then build a snapshot:
        - roles: list[str]
        - permissions: list[str] (sorted, unique)
        - token_version: int (0: user not found/disabled/deleted, >=1: valid authentication state)
        """
        stmt = (
            select(User)
            .where(User.id == user_id)
            .options(
                selectinload(User.roles).selectinload(Role.permissions)
            )
        )
        user = db.execute(stmt).scalars().first()

        # Single source of truth deciding authentication validity
        is_deleted = bool(getattr(user, "is_deleted", False))
        is_active = bool(getattr(user, "is_active", True))
        if not user or is_deleted or not is_active:
            # Service/guards layer decides what to raise
            return [], [], 0

        roles, permissions = self._build_authz_snapshot(user)
        token_version = getattr(user, "token_version", 1)

        return roles, permissions, token_version

    # ===== Private helpers =====
    def _build_authz_snapshot(self, user: User) -> tuple[list[str], list[str]]:
        """
        Build authz snapshot from ORM relationships (domain flattening)
        """
        roles_rel: list[Role] = user.roles

        role_names: list[str] = [r.name for r in roles_rel]

        permission_codes: set[str] = set()
        for role in roles_rel:
            for perm in role.permissions:
                permission_codes.add(perm.code)

        permission_list: list[str] = sorted(permission_codes)
        return role_names, permission_list
