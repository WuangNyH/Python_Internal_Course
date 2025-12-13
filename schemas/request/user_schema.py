from datetime import date

from pydantic import BaseModel, Field, model_validator, field_validator


class UserCreate(BaseModel):
    name: str
    age: int
    address: str | None = None

# class UserCreate(BaseModel):
#     name: str = Field(
#         min_length=2,
#         max_length=50,
#         pattern=r"^[A-Za-z ]+$",
#         description="User name (2-50 characters) contains only letters",
#         examples=["Taro Kun"]
#     )
#     age: int
#     address: str | None = None

# class UserCreate(BaseModel):
#     name: str = Field(
#         min_length=2,
#         max_length=50,
#         pattern=r"^[A-Za-z ]+$",
#         description="User name (2-50 characters) contains only letters",
#         examples=["Taro Kun"]
#     )
#     age: int = Field(ge=0, le=150)
#     address: str | None = None

# class UserCreate(BaseModel):
#     name: str = Field(min_length=2, max_length=50)
#     age: int = Field(ge=1, le=150)
#     address: str | None = None
#
#     @field_validator("name")
#     @classmethod
#     def name_not_empty(cls, v: str):
#         if not v.strip():
#             raise ValueError("Name cannot be empty")
#         return v.strip()
#
#
# class BookingCreate(BaseModel):
#     start_date: date
#     end_date: date
#
#     @model_validator(mode="after")
#     def check_date_range(self):
#         if self.start_date >= self.end_date:
#             raise ValueError("end_date must be after start_date")
#         return self
