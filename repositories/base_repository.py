from typing import Any, Generic, Type, TypeVar, Mapping, Sequence, cast, List
from sqlalchemy import select, func, Select, ColumnElement
from sqlalchemy.orm import Session

from core.http.pagination import PageParams, PageMeta
from core.http.sorting import SortSpec
from models.base import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    def __init__(self, model: Type[ModelType]):
        self.model = model

    # -------- READ --------
    def get_by_id(
            self, db: Session, entity_id: Any
    ) -> ModelType | None:
        stmt = select(self.model).where(self.model.id == entity_id)  # type: ignore[attr-defined]
        return db.execute(stmt).scalars().first()

    def get_alive_by_id(
            self, db: Session, entity_id: Any
    ) -> ModelType | None:
        stmt = select(self.model).where(self.model.id == entity_id)  # type: ignore[attr-defined]
        stmt = self._apply_alive_filter(stmt)
        return db.execute(stmt).scalars().first()

    def list(
            self, db: Session, *, offset: int = 0, limit: int = 100
    ) -> Sequence[ModelType]:
        stmt = select(self.model).offset(offset).limit(limit)
        return list(db.execute(stmt).scalars().all())

    def list_active(
            self, db: Session, *, offset: int = 0, limit: int = 100
    ) -> Sequence[ModelType]:
        stmt = select(self.model)
        stmt = self._apply_alive_filter(stmt)
        stmt = stmt.offset(offset).limit(limit)
        return list(db.execute(stmt).scalars().all())

    def exists_by_id(self, db: Session, entity_id: Any) -> bool:
        stmt = select(func.count()).select_from(self.model).where(
            self.model.id == entity_id)  # type: ignore[attr-defined]
        return (db.execute(stmt).scalar_one() or 0) > 0

    def exists_active_by_id(self, db: Session, entity_id: Any) -> bool:
        stmt = select(func.count()).select_from(self.model).where(
            self.model.id == entity_id  # type: ignore[attr-defined]
        )
        stmt = self._apply_alive_filter(stmt)
        return (db.execute(stmt).scalar_one() or 0) > 0

    # -------- WRITE --------
    def create(self, db: Session, entity: ModelType) -> ModelType:
        db.add(entity)
        db.flush()
        db.refresh(entity)
        return entity

    def update(
            self,
            db: Session,
            entity: ModelType,
            data: dict[str, Any],
            *,
            refresh: bool = True,
    ) -> ModelType:
        # Strict guard: do not update soft-deleted entity
        if hasattr(entity, "is_deleted") and bool(
                getattr(entity, "is_deleted", False)):
            raise RuntimeError("Cannot update soft-deleted entity")

        for field, value in data.items():
            setattr(entity, field, value)

        db.flush()
        if refresh:
            db.refresh(entity)
        return entity

    def delete(self, db: Session, entity: ModelType) -> None:
        db.delete(entity)
        db.flush()

    def soft_delete(
            self,
            db: Session,
            entity: ModelType,
            *,
            actor_user_id: Any | None = None
    ) -> None:
        if hasattr(entity, "mark_deleted"):
            entity.mark_deleted(actor_user_id=actor_user_id)  # type: ignore[misc]
            db.flush()
            return

        if self._supports_soft_delete():
            setattr(entity, "is_deleted", True)
            if hasattr(entity, "deleted_by"):
                setattr(entity, "deleted_by", actor_user_id)
            if hasattr(entity, "deleted_at"):
                setattr(entity, "deleted_at", func.now())
            db.flush()
            return

        # fallback
        self.delete(db, entity)

    # -------- GENERIC QUERY HELPERS (for search) --------
    def apply_paging(self, stmt: Select, *, page: PageParams) -> Select:
        return stmt.offset(page.offset).limit(page.limit)

    def count(self, db: Session, stmt: Select) -> int:
        # count(*) trên subquery để giữ đúng filter/join
        count_stmt = select(func.count()).select_from(stmt.subquery())
        return int(db.execute(count_stmt).scalar() or 0)

    def build_page_meta(
            self, *, total: int, page: PageParams
    ) -> PageMeta:
        return PageMeta.from_total(
            total=total, page=page.page, page_size=page.page_size)

    def apply_sort(
            self,
            stmt: Select,
            *,
            sorts: Sequence[SortSpec] | None,
            allowed_sort_fields: Mapping[str, ColumnElement[Any]],
            default_sorts: Sequence[SortSpec] | None = None,
    ) -> Select:

        # 1) sort specs (new style)
        if sorts:
            stmt = self._apply_sort_specs(
                stmt,
                sorts=sorts,
                allowed_sort_fields=allowed_sort_fields
            )
            return stmt

        # 2) defaults
        if default_sorts:
            stmt = self._apply_sort_specs(
                stmt,
                sorts=default_sorts,
                allowed_sort_fields=allowed_sort_fields
            )
            return stmt

        # 3) safe fallback (only if field exists in allowlist)
        fallback = SortSpec(field="created_at", direction="desc")
        return self._apply_sort_specs(
            stmt,
            sorts=[fallback],
            allowed_sort_fields=allowed_sort_fields
        )

    # -------- PROTECTED HELPERS --------

    # ===== Soft-delete support (opt-in by model) =====
    def _supports_soft_delete(self) -> bool:
        return hasattr(self.model, "is_deleted")

    def _apply_alive_filter(self, stmt: Select) -> Select:
        if self._supports_soft_delete():
            stmt = stmt.where(getattr(self.model, "is_deleted").is_(False))
        return stmt

    # ===== Sort =====
    def _apply_sort_specs(
            self,
            stmt: Select,
            *,
            sorts: Sequence[SortSpec],
            allowed_sort_fields: Mapping[str, ColumnElement[Any]],
    ) -> Select:
        for sp in sorts:
            field = str(sp.field).strip()
            if not field:
                continue

            col = allowed_sort_fields.get(field)
            if col is None:
                continue

            stmt = stmt.order_by(col.desc() if sp.is_desc else col.asc())

        return stmt

    # ===== Common search pipeline =====
    def _execute_search(
            self,
            *,
            db: Session,
            stmt: Select,
            total: int,
            page: PageParams,
            sort_specs: Sequence[SortSpec] | None,
            allowed_sort_fields: Mapping[str, ColumnElement[Any]],
            default_sorts: Sequence[SortSpec],
    ) -> tuple[List[ModelType], int, PageMeta]:
        """
        Execute common search pipeline:
        - apply sort
        - apply paging
        - execute
        - build PageMeta

        :return: tuple[items, total, meta]
        """
        stmt = self.apply_sort(
            stmt,
            sorts=sort_specs,
            allowed_sort_fields=allowed_sort_fields,
            default_sorts=default_sorts,
        )

        stmt = self.apply_paging(stmt, page=page)

        items = cast(list[ModelType], db.execute(stmt).scalars().all())
        meta = self.build_page_meta(total=total, page=page)
        return items, total, meta
