from datetime import datetime
from typing import Any

from sqlalchemy import select, or_
from sqlalchemy.orm import Session

from core.http.pagination import PageMeta, PageParams
from core.http.sorting import SortSpec, parse_sort
from models.user import User
from repositories.base_repository import BaseRepository
from schemas.request.user_schema import UserSearchParams


class UserRepository(BaseRepository[User]):
    # Whitelist field cho sort (tránh sort injection)
    _SORT_FIELDS: dict[str, Any] = {
        "id": User.id,
        "email": User.email,
        "is_active": User.is_active,
        "created_at": User.created_at,
        "updated_at": User.updated_at,
    }

    def __init__(self):
        super().__init__(User)

    def get_by_email(self, db: Session, *, email: str) -> User | None:
        stmt = select(User).where(User.email == email)
        stmt = self._apply_alive_filter(stmt)  # exclude soft-deleted
        return db.execute(stmt).scalars().first()

    def exists_by_email(self, db: Session, *, email: str) -> bool:
        stmt = select(User.id).where(User.email == email)
        stmt = self._apply_alive_filter(stmt)  # exclude soft-deleted
        return db.execute(stmt.limit(1)).scalar_one_or_none() is not None

    def search(
            self,
            db: Session,
            *,
            params: UserSearchParams,
    ) -> tuple[list[User], int, PageMeta]:
        """
        Searches for users based on the specified parameters, applying various filters,
        sorting, and pagination to the data.

        The method utilizes a database session to execute a query that finds users
        that match the given criteria, processes the query statement by applying
        filters and sorting, and then applies pagination to return a subset of results.

        :param db: A SQLAlchemy session object used to execute the query.
        :param params: Data structure containing parameters for filtering, sorting,
            and paginating the results.
        :return: tuple[items, total, meta]
        """
        stmt = select(User)
        stmt = self._apply_alive_filter(stmt)
        stmt = self._apply_filters(stmt, params)

        total = self.count(db, stmt)

        # Build PageParams
        page_params = PageParams(page=params.page, page_size=params.page_size)

        # Enterprise style sort string: sort="created_at,-email"
        sort_specs = parse_sort(params.sort) if params.sort else None

        # Apply sort with default = created_at desc
        return self._execute_search(
            db=db,
            stmt=stmt,
            total=total,
            page=page_params,
            sort_specs=sort_specs,
            allowed_sort_fields=self._SORT_FIELDS,
            default_sorts=[SortSpec(field="created_at", direction="desc")],
        )

    # ===== Internal helpers =====
    def _apply_filters(self, stmt, params: UserSearchParams):
        # Filter exact email
        email = getattr(params, "email", None)
        if email:
            stmt = stmt.where(User.email == email)

        # Keyword search (q) - search email
        q = getattr(params, "q", None)
        if q:
            like = f"%{str(q).strip()}%"
            stmt = stmt.where(or_(User.email.ilike(like)))

        is_active = getattr(params, "is_active", None)
        if is_active is not None:
            stmt = stmt.where(User.is_active == bool(is_active))

        # created_at range
        created_from: datetime | None = getattr(params, "created_from", None)
        created_to: datetime | None = getattr(params, "created_to", None)
        if created_from:
            stmt = stmt.where(User.created_at >= created_from)
        if created_to:
            stmt = stmt.where(User.created_at <= created_to)

        return stmt
