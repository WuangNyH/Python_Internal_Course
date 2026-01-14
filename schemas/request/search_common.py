from datetime import datetime
from typing import Any, ClassVar
from pydantic import BaseModel, Field, field_validator, model_validator


def _parse_dt(v: Any) -> datetime | None:
    """
    Accept:
    - None
    - datetime
    - ISO 8601 string (supports trailing 'Z')
    """
    if v is None or v == "":
        return None
    if isinstance(v, datetime):
        return v
    if isinstance(v, str):
        s = v.strip()
        if not s:
            return None
        # allow "Z"
        if s.endswith("Z"):
            s = s[:-1] + "+00:00"
        try:
            return datetime.fromisoformat(s)
        except ValueError:
            return None
    return None


class PagedSortParams(BaseModel):
    page: int = Field(default=1, description="Page number (begin from 1)")
    page_size: int = Field(default=20, description="Page size")
    sort: str | None = Field(
        default=None,
        description='Sort spec, e.g. "created_at,-id" (comma-separated)',
    )

    MAX_PAGE_SIZE: ClassVar[int] = 200

    @field_validator("page", mode="before")
    @classmethod
    def parse_page(cls, v: Any) -> int:
        try:
            n = int(v)
        except (TypeError, ValueError):
            return 1
        return n if n > 0 else 1

    @field_validator("page_size", mode="before")
    @classmethod
    def parse_page_size(cls, v: Any) -> int:
        try:
            n = int(v)
        except (TypeError, ValueError):
            return 20
        return n if n > 0 else 20

    @field_validator("page_size", mode="after")
    @classmethod
    def enforce_page_size_limit(cls, v: int) -> int:
        # Enforce limit in one place, but configurable per schema via class attr
        if v > int(getattr(cls, "MAX_PAGE_SIZE", 200)):
            raise ValueError(f">>>>> page_size must be <= {int(getattr(cls, 'MAX_PAGE_SIZE', 200))}")
        return v


class StrictSortParams(BaseModel):
    """
    Schema con có thể override:
      - SORT_FIELD_NAME: tên field sort trong schema (default: 'sort')
      - ALLOWED_SORT_FIELDS: allowlist các field được sort
    """
    SORT_FIELD_NAME: ClassVar[str] = "sort"
    ALLOWED_SORT_FIELDS: ClassVar[set[str]] = set()

    @model_validator(mode="after")
    def validate_sort_strict(self):
        sort_field = str(getattr(self.__class__, "SORT_FIELD_NAME", "sort"))
        raw = getattr(self, sort_field, None)

        # normalize
        if raw is None:
            return self

        s = str(raw).strip()
        if not s:
            setattr(self, sort_field, None)
            return self

        allowed = set(getattr(self.__class__, "ALLOWED_SORT_FIELDS", set()))
        if not allowed:
            raise ValueError(">>>>> ALLOWED_SORT_FIELDS is not configured for strict sort validation")

        parts = [p.strip() for p in s.split(",")]
        if any(not p for p in parts):
            raise ValueError('>>>>> Invalid sort format. Example: "created_at,-id"')

        for p in parts:
            field = p[1:] if p.startswith("-") else p
            if field not in allowed:
                raise ValueError(f">>>>> Invalid sort field '{field}'. Allowed: {sorted(allowed)}")

        # write-back normalized value
        setattr(self, sort_field, s)
        return self


class CreatedRangeParams(BaseModel):
    created_from: datetime | None = Field(default=None, description="created_at >= created_from (ISO 8601)")
    created_to: datetime | None = Field(default=None, description="created_at <= created_to (ISO 8601)")

    @field_validator("created_from", "created_to", mode="before")
    @classmethod
    def parse_datetime(cls, v: Any) -> datetime | None:
        return _parse_dt(v)
