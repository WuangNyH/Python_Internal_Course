from fastapi import APIRouter, Depends, Request, Response, status
from sqlalchemy.orm import Session

from dependencies.db import get_db
from schemas.request.student_schema import StudentCreate, StudentUpdate
from schemas.response.base import SuccessResponse
from schemas.response.error_response import ErrorResponse
from schemas.response.student_out_schema import StudentOut
from services.student_service import StudentService

student_router = APIRouter()
service = StudentService()


@student_router.get("", response_model=SuccessResponse[list[StudentOut]])
def list_students(
        request: Request,
        offset: int = 0,
        limit: int = 100,
        db: Session = Depends(get_db),
) -> SuccessResponse[list[StudentOut]]:
    students = service.list_students(db, offset=offset, limit=limit)
    data = [StudentOut.model_validate(student) for student in students]
    return SuccessResponse(data=data, trace_id=request.state.trace_id)


@student_router.get(
    "/{student_id:int}",
    response_model=SuccessResponse[StudentOut],
    responses={404: {"model": ErrorResponse, "description": "Student not found"}},
)
def get_student(
        request: Request,
        student_id: int,
        db: Session = Depends(get_db),
) -> SuccessResponse[StudentOut]:
    student = service.get_student(db, student_id)
    return SuccessResponse(
        data=StudentOut.model_validate(student),
        trace_id=request.state.trace_id,
    )


@student_router.get(
    "/search",
    response_model=SuccessResponse[list[StudentOut]],
    responses={
        400: {
            "model": ErrorResponse,
            "description": "Invalid search parameters (business rule violation)"
        }
    }
)
def search_students(
        request: Request,
        keyword: str | None = None,
        min_age: int | None = None,
        max_age: int | None = None,
        offset: int = 0,
        limit: int = 100,
        db: Session = Depends(get_db),
) -> SuccessResponse[list[StudentOut]]:
    students = service.search_students(
        db,
        keyword=keyword,
        min_age=min_age,
        max_age=max_age,
        offset=offset,
        limit=limit,
    )
    data = [StudentOut.model_validate(s) for s in students]
    return SuccessResponse(data=data, trace_id=request.state.trace_id)


@student_router.post(
    "",
    response_model=SuccessResponse[StudentOut],
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"model": ErrorResponse, "description": "Business validation error"},
        409: {"model": ErrorResponse, "description": "Email already exists"}
    },
)
def create_student(
        data: StudentCreate,
        request: Request,
        response: Response,
        db: Session = Depends(get_db),
) -> SuccessResponse[StudentOut]:
    student = service.create_student(db, data)

    # Set Location header
    location = request.url_for("get_student", student_id=student.id)
    response.headers["location"] = str(location)

    return SuccessResponse(
        data=StudentOut.model_validate(student),
        message="Student created successfully",
        trace_id=request.state.trace_id,
    )


@student_router.patch(
    "/{student_id}",
    response_model=SuccessResponse[StudentOut],
    responses={
        400: {"model": ErrorResponse, "description": "Business validation error"},
        404: {"model": ErrorResponse, "description": "Not found"},
    }
)
def update_student(
        request: Request,
        student_id: int,
        data: StudentUpdate,
        db: Session = Depends(get_db),
) -> SuccessResponse[StudentOut]:
    student = service.update_student(db, student_id, data)
    return SuccessResponse(
        data=StudentOut.model_validate(student),
        message="Student updated successfully",
        trace_id=request.state.trace_id,
    )


@student_router.delete(
    "/{student_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={404: {"model": ErrorResponse, "description": "Not found"}},
)
def delete_student(
        request: Request,
        response: Response,
        student_id: int,
        db: Session = Depends(get_db),
) -> None:
    service.delete_student(db, student_id)
    response.headers["x-trace-id"] = request.state.trace_id
    return None
