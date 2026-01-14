import re
from typing import Any, ClassVar
from pydantic import BaseModel, EmailStr, Field, field_validator

from core.search.constants import MAX_KEYWORD_LENGTH
from schemas.request.search_common import CreatedRangeParams, PagedSortParams, StrictSortParams


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    is_active: bool = True


class UserUpdate(BaseModel):
    # PATCH semantics: field nào None => không update
    email: EmailStr | None = None
    password: str | None = Field(default=None, min_length=8, max_length=128)
    is_active: bool | None = None


class UserSearchParams(PagedSortParams, StrictSortParams, CreatedRangeParams):
    ALLOWED_SORT_FIELDS: ClassVar[set[str]] = {"id", "email", "is_active", "created_at", "updated_at"}

    # ===== Filters =====
    email: EmailStr | None = Field(default=None, description="Exact email")
    # Keyword search (q), ví dụ search email

    q: str | None = Field(
        default=None,
        description="Keyword search (email contains)",
        min_length=1,
    )

    is_active: bool | None = None

    @field_validator("q", mode="before")
    @classmethod
    def normalize_q(cls, v: Any) -> str | None:
        if v is None:
            return None
        s = str(v).strip()
        if not s:
            return None

        # collapse whitespace -> protect performance/log size
        s = re.sub(r"\s+", " ", s)
        return s[:MAX_KEYWORD_LENGTH]
