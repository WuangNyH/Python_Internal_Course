from sqlalchemy.orm import Session

from core.exceptions.student_exception import StudentNotFoundException, InvalidStudentSearchAgeRangeException, \
    StudentEmailAlreadyExistsException, InvalidStudentAgeException
from models.student import Student
from repositories.student_repository import StudentRepository
from schemas.request.student_schema import StudentCreate, StudentUpdate

import logging

logger = logging.getLogger(__name__)


class StudentService:

    def __init__(self):
        self.repo = StudentRepository()

    # -------- READ --------
    def get_student(self, db: Session, student_id: int) -> Student:
        student = self.repo.get_by_id(db, student_id)
        if not student:
            raise StudentNotFoundException(student_id)
        return student

    def list_students(self, db: Session, offset: int = 0, limit: int = 100) -> list[Student]:
        return self.repo.list(db, offset=offset, limit=limit)

    def search_students(
            self,
            db: Session,
            *,
            keyword: str | None = None,
            min_age: int | None = None,
            max_age: int | None = None,
            offset: int = 0,
            limit: int = 100,
    ) -> list[Student]:
        # Rule nghiệp vụ đơn giản: min_age không được lớn hơn max_age
        if min_age is not None and max_age is not None and min_age > max_age:
            raise InvalidStudentSearchAgeRangeException(min_age, max_age)

        return self.repo.search(
            db,
            keyword=keyword,
            min_age=min_age,
            max_age=max_age,
            offset=offset,
            limit=limit,
        )

    # -------- WRITE --------
    def create_student(self, db: Session, data: StudentCreate) -> Student:
        # Rule nghiệp vụ: email unique
        existed = self.repo.get_by_email(db, str(data.email))
        if existed:
            raise StudentEmailAlreadyExistsException(str(data.email))

        # Rule nghiệp vụ: tuổi hợp lệ
        if data.age < 18:
            raise InvalidStudentAgeException(data.age)

        student = Student(**data.model_dump())
        return self.repo.create(db, student)

    # PATCH
    def update_student(self, db: Session, student_id: int, data: StudentUpdate) -> Student:
        student = self.get_student(db, student_id)

        # Rule nghiệp vụ: không cho update age dưới 18
        if data.age is not None and data.age < 18:
            raise InvalidStudentAgeException(data.age)

        # exclude_unset=True: chỉ lấy field client gửi
        updated_data = data.model_dump(exclude_unset=True)

        return self.repo.update(db, student, updated_data)

    def delete_student(self, db: Session, student_id: int) -> None:
        student = self.get_student(db, student_id)
        self.repo.delete(db, student)
