from pydantic import BaseModel, Field, model_validator
from math import ceil


class PageParams(BaseModel):
    """
    Paging input từ query params
    """
    page: int = Field(default=1, ge=1, description="Page number (1-based)")
    page_size: int = Field(default=20, ge=1, le=100, description="Items per page")

    @model_validator(mode="after")
    def _validate_page(self) -> "PageParams":
        # Có thể bổ sung thêm rule nghiệp vụ nếu cần
        return self

    @property
    def offset(self) -> int:
        """
        Offset dùng cho SQLAlchemy
        """
        return (self.page - 1) * self.page_size

    @property
    def limit(self) -> int:
        return self.page_size


class PageMeta(BaseModel):
    """
    Metadata trả về cho client
    """
    total: int
    page: int
    page_size: int
    total_pages: int
    has_next: bool
    has_prev: bool

    @classmethod
    def from_total(
        cls,
        *,
        total: int,
        page: int,
        page_size: int,
    ) -> "PageMeta":
        total_pages = ceil(total / page_size) if page_size > 0 else 0

        return cls(
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
            has_next=page < total_pages,
            has_prev=page > 1,
        )
