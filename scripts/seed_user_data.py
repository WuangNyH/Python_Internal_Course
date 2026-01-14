from dataclasses import dataclass
from typing import Iterable

from sqlalchemy import select
from sqlalchemy.orm import Session

from configs.database import SessionLocal
from core.security.permissions import Permissions
from security.password import hash_password

from models.user import User
from models.role import Role
from models.permission import Permission


# =========================
# Seed definitions
# =========================

@dataclass(frozen=True)
class SeedRole:
    name: str
    permissions: tuple[str, ...]


@dataclass(frozen=True)
class SeedUser:
    email: str
    password: str
    roles: tuple[str, ...]
    is_active: bool = True
    token_version: int = 1


# =========================
# Permission codes
# =========================

PERM_USER_READ = "user:read"
PERM_USER_WRITE = "user:write"
PERM_USER_DELETE = "user:delete"

PERM_STUDENT_READ = "student:read"
PERM_STUDENT_WRITE = "student:write"

PERM_TASK_READ = "task:read"
PERM_TASK_WRITE = "task:write"


# =========================
# Roles
# =========================

SEED_ROLES: tuple[SeedRole, ...] = (
    SeedRole(
        name="ADMIN",
        permissions=(
            Permissions.USER_READ,
            Permissions.USER_WRITE,
            Permissions.USER_DELETE,
            Permissions.STUDENT_READ,
            Permissions.STUDENT_WRITE,
            Permissions.STUDENT_DELETE,
            Permissions.TASK_READ,
            Permissions.TASK_WRITE,
            Permissions.TASK_DELETE,
        ),
    ),
    SeedRole(
        name="HR_MANAGER",
        permissions=(
            Permissions.USER_READ,
            Permissions.USER_WRITE,
            Permissions.STUDENT_READ,
            Permissions.STUDENT_WRITE,
            Permissions.STUDENT_DELETE,
            Permissions.TASK_READ,
            Permissions.TASK_WRITE,
            Permissions.TASK_DELETE,
        ),
    ),
    SeedRole(
        name="TEACHER",
        permissions=(
            Permissions.STUDENT_READ,
            Permissions.STUDENT_WRITE,
            Permissions.TASK_READ,
            Permissions.TASK_WRITE,
            Permissions.TASK_DELETE,
        ),
    ),
    SeedRole(
        name="STAFF",
        permissions=(
            Permissions.STUDENT_READ,
            Permissions.TASK_READ,
        ),
    ),
    SeedRole(
        name="STUDENT",
        permissions=(
            Permissions.STUDENT_READ,
        ),
    ),
)


# =========================
# Users
# =========================

SEED_USERS: tuple[SeedUser, ...] = (
    SeedUser("admin1@example.com", "Admin@123456", ("ADMIN",)),
    SeedUser("admin2@example.com", "Admin@123456", ("ADMIN",)),
    SeedUser("manager1@example.com", "Manager@123456", ("HR_MANAGER",)),
    SeedUser("manager2@example.com", "Manager@123456", ("HR_MANAGER",)),
    SeedUser("teacher1@example.com", "Teacher@123456", ("TEACHER",)),
    SeedUser("teacher2@example.com", "Teacher@123456", ("TEACHER",)),
    SeedUser("staff1@example.com", "Staff@123456", ("STAFF",)),
    SeedUser("staff2@example.com", "Staff@123456", ("STAFF",)),
    SeedUser("student1@example.com", "Student@123456", ("STUDENT",)),
    SeedUser("student2@example.com", "Student@123456", ("STUDENT",)),
)


# =========================
# Upsert helpers
# =========================

def upsert_permissions(
        db: Session, codes: Iterable[str]) -> dict[str, Permission]:
    existing = db.execute(
        select(Permission).where(Permission.code.in_(codes))
    ).scalars().all()
    by_code = {p.code: p for p in existing}

    for code in codes:
        if code not in by_code:
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
    names = [r.name for r in roles]
    existing = db.execute(
        select(Role).where(Role.name.in_(names))
    ).scalars().all()
    by_name = {r.name: r for r in existing}

    for seed in roles:
        role = by_name.get(seed.name)
        if role is None:
            role = Role(name=seed.name)
            db.add(role)
            by_name[seed.name] = role

        role.permissions = [
            permissions_by_code[c]
            for c in seed.permissions
            if c in permissions_by_code
        ]

    db.flush()
    return by_name


def upsert_users(
    db: Session,
    users: Iterable[SeedUser],
    roles_by_name: dict[str, Role],
) -> None:
    emails = [u.email for u in users]
    existing = db.execute(
        select(User).where(User.email.in_(emails))
    ).scalars().all()
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
        else:
            user.is_active = seed.is_active
            user.token_version = seed.token_version
            # Không reset password nếu user đã tồn tại (enterprise safe)

        user.roles = [
            roles_by_name[r]
            for r in seed.roles
            if r in roles_by_name
        ]

    db.flush()


# =========================
# Main runner
# =========================

def seed_data() -> None:
    db = SessionLocal()
    try:
        perm_codes = {c for r in SEED_ROLES for c in r.permissions}
        perms = upsert_permissions(db, perm_codes)
        roles = upsert_roles(db, SEED_ROLES, perms)

        upsert_users(db, SEED_USERS, roles)

        db.commit()
        print(">>>>>> Seed users / roles / permissions completed")

    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_data()
