from dataclasses import dataclass
from typing import Iterable

from sqlalchemy import select
from sqlalchemy.orm import Session

from configs.database import SessionLocal
from security.password import hash_password

from models import Permission, Role, User


@dataclass(frozen=True)
class SeedRole:
    name: str
    permission_codes: tuple[str, ...]


@dataclass(frozen=True)
class SeedUser:
    email: str
    password: str
    role_names: tuple[str, ...]
    is_active: bool = True
    token_version: int = 1


PERM_STUDENT_READ = "student:read"
PERM_STUDENT_WRITE = "student:write"
PERM_STUDENT_DELETE = "student:delete"

PERM_TASK_READ = "task:read"
PERM_TASK_WRITE = "task:write"
PERM_TASK_DELETE = "task:delete"

DEFAULT_PERMISSIONS: tuple[str, ...] = (
    # Students
    PERM_STUDENT_READ,
    PERM_STUDENT_WRITE,
    PERM_STUDENT_DELETE,
    # Tasks
    PERM_TASK_READ,
    PERM_TASK_WRITE,
    PERM_TASK_DELETE,
)

DEFAULT_ROLES: tuple[SeedRole, ...] = (
    SeedRole(
        name="ADMIN",
        permission_codes=DEFAULT_PERMISSIONS,
    ),
    SeedRole(
        name="TEACHER",
        permission_codes=(
            PERM_STUDENT_READ,
            PERM_STUDENT_WRITE,
            PERM_TASK_READ,
            PERM_TASK_WRITE,
        ),
    ),
    SeedRole(
        name="STUDENT",
        permission_codes=(
            PERM_STUDENT_READ,
            PERM_TASK_READ,
        ),
    ),
)

DEFAULT_USERS: tuple[SeedUser, ...] = (
    SeedUser(
        email="admin@example.com",
        password="Admin@123456",
        role_names=("ADMIN",),
    ),
    SeedUser(
        email="teacher@example.com",
        password="Teacher@123456",
        role_names=("TEACHER",),
    ),
    SeedUser(
        email="student@example.com",
        password="Student@123456",
        role_names=("STUDENT",),
    ),
)


# Upsert helpers (idempotent)
def upsert_permissions(db: Session, codes: Iterable[str]) -> dict[str, Permission]:
    existing = db.execute(select(Permission).where(Permission.code.in_(list(codes)))).scalars().all()
    by_code = {p.code: p for p in existing}

    for code in codes:
        if code in by_code:
            continue
        p = Permission(code=code)
        db.add(p)
        by_code[code] = p

    db.flush()
    return by_code


def upsert_roles(
        db: Session,
        roles: Iterable[SeedRole],
        permissions_by_code: dict[str, Permission],
) -> dict[str, Role]:
    role_names = [r.name for r in roles]
    existing = db.execute(select(Role).where(Role.name.in_(role_names))).scalars().all()
    by_name = {r.name: r for r in existing}

    for seed in roles:
        role = by_name.get(seed.name)
        if role is None:
            role = Role(name=seed.name)
            db.add(role)
            by_name[seed.name] = role

        # Gán permissions theo code (many-to-many)
        desired_perms = [permissions_by_code[c] for c in seed.permission_codes if c in permissions_by_code]
        # Tránh duplicate trong list relationship
        role.permissions = list({p.code: p for p in desired_perms}.values())

    db.flush()
    return by_name


def upsert_users(
        db: Session,
        users: Iterable[SeedUser],
        roles_by_name: dict[str, Role],
) -> dict[str, User]:
    emails = [u.email for u in users]
    existing = db.execute(select(User).where(User.email.in_(emails))).scalars().all()
    by_email = {u.email: u for u in existing}

    for seed in users:
        user = by_email.get(seed.email)
        if user is None:
            user = User(
                email=seed.email,
                hashed_password=hash_password(seed.password),
                is_active=seed.is_active,
                token_version=seed.token_version,
            )
            db.add(user)
            by_email[seed.email] = user
        else:
            # Đồng bộ trạng thái cơ bản
            user.is_active = seed.is_active
            user.token_version = seed.token_version

        # Gán roles theo name (many-to-many)
        desired_roles = [roles_by_name[n] for n in seed.role_names if n in roles_by_name]
        user.roles = list({r.name: r for r in desired_roles}.values())

    db.flush()
    return by_email


# Main runner
def seed() -> None:
    db = SessionLocal()
    try:
        permissions_by_code = upsert_permissions(db, DEFAULT_PERMISSIONS)
        upsert_roles(db, DEFAULT_ROLES, permissions_by_code)
        roles_by_name = db.execute(select(Role)).scalars().all()
        roles_by_name_map = {r.name: r for r in roles_by_name}

        upsert_users(db, DEFAULT_USERS, roles_by_name_map)

        db.commit()

        print("Seed users/roles/permissions: OK")
        print("Created/ensured users:")
        for u in DEFAULT_USERS:
            print(f" - {u.email} / {u.password} (roles={u.role_names})")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()
