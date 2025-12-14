from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from configs.database import Base
from models.TimeMixin import TimeMixin


class Student(TimeMixin, Base):
    __tablename__ = "students"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    full_name: Mapped[str] = mapped_column(String(100), nullable=False)
    age: Mapped[int] = mapped_column(nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    phone_number: Mapped[str | None] = mapped_column(String(20))
