from sqlalchemy.orm import Session, selectinload
from sqlalchemy import select

from models.user import User
from models.role import Role


class AuthRepository:
    def get_user_credentials_by_email(self, db: Session, email: str) -> User | None:
        stmt = select(User).where(User.email == email)
        return db.execute(stmt).scalars().first()

    def get_authz_snapshot(self, db: Session, user_id: int) -> tuple[list[str], list[str], int]:
        stmt = (
            select(User)
            .where(User.id == user_id)
            .options(
                selectinload(User.roles).selectinload(Role.permissions)
            )
        )
        user = db.execute(stmt).scalars().first()
        if not user:
            # Service sẽ quyết định raise gì
            return [], [], 0

        roles = [r.name for r in user.roles]
        permissions = sorted({p.code for r in user.roles for p in r.permissions})
        token_version = getattr(user, "token_version", 1)
        return roles, permissions, token_version
