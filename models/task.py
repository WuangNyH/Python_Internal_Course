from sqlalchemy import Column, Integer, String, Boolean, ForeignKey

from configs.database import Base
from models.TimeMixin import TimeMixin


class Task(TimeMixin, Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)

    title = Column(String(200), nullable=False)
    is_done = Column(Boolean, nullable=False, default=False)

    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
