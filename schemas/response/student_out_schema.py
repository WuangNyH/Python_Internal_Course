from datetime import datetime
from pydantic import EmailStr

from schemas.response.base import TimestampMixin


class StudentOut(TimestampMixin):
    id: int
    full_name: str
    age: int
    email: EmailStr
    phone_number: str | None = None
    created_at: datetime
    updated_at: datetime
