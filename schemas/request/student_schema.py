from datetime import datetime
from pydantic import BaseModel, EmailStr


class StudentCreate(BaseModel):
    full_name: str
    age: int
    email: EmailStr


class StudentUpdate(BaseModel):
    full_name: str | None = None
    age: int | None = None


class StudentOut(BaseModel):
    id: int
    full_name: str
    age: int
    email: EmailStr
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True