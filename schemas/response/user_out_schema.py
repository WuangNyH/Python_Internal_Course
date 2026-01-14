from uuid import UUID
from pydantic import EmailStr, BaseModel

from schemas.response.base import TimestampMixin


class UserOut(TimestampMixin):
    id: UUID
    email: EmailStr
    is_active: bool


class UserListOut(BaseModel):
    items: list[UserOut]
    total: int
    page: int
    page_size: int
