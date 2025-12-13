from pydantic import BaseModel, EmailStr, HttpUrl


class UserOut(BaseModel):
    id: int
    name: str
    age: int

# class UserOut(BaseModel):
#     email: EmailStr
#     avatar_url: HttpUrl | None = None
