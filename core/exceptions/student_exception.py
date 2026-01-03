from http import HTTPStatus

from core.exceptions.base import BusinessException


class StudentNotFoundException(BusinessException):
    def __init__(self, student_id: int):
        super().__init__(
            message=f"Student {student_id} not found",
            error_code="STUDENT_NOT_FOUND",
            status_code=HTTPStatus.NOT_FOUND,
            extra={"student_id": student_id},
        )


class InvalidStudentSearchAgeRangeException(BusinessException):
    def __init__(self, min_age: int, max_age: int):
        super().__init__(
            message="min_age must be less than or equal to max_age",
            error_code="INVALID_STUDENT_SEARCH_AGE_RANGE",
            status_code=HTTPStatus.BAD_REQUEST,
            extra={
                "min_age": min_age,
                "max_age": max_age,
            },
        )


class StudentEmailAlreadyExistsException(BusinessException):
    def __init__(self, email: str):
        super().__init__(
            message="Email already exists",
            error_code="EMAIL_ALREADY_EXISTS",
            status_code=HTTPStatus.CONFLICT,
            extra={"email": email},
        )


class InvalidStudentAgeException(BusinessException):
    def __init__(self, age: int):
        super().__init__(
            message="Age must be >= 18",
            error_code="INVALID_STUDENT_AGE",
            status_code=HTTPStatus.BAD_REQUEST,
            extra={"age": age},
        )
