from fastapi import APIRouter, Depends, Request, Response, status
from fastapi.params import Security
from sqlalchemy.orm import Session

from core.openapi_responses import UNAUTHORIZED_401, INTERNAL_500, AUTH_COMMON_RESPONSES, NOT_FOUND_404, \
    BAD_REQUEST_400, AUTHZ_COMMON_RESPONSES, CONFLICT_409, FORBIDDEN_403
from core.responses import success_response
from dependencies.db import get_db
from schemas.common import EmptyData
from schemas.request.student_schema import StudentCreate, StudentUpdate
from schemas.response.base import SuccessResponse
from schemas.response.student_out_schema import StudentOut
from security.dependencies import require_current_user
from security.guards import require_roles, require_permissions
from security.principals import CurrentUser
from security.schemes import bearer_scheme
from services.student_service import StudentService

student_router = APIRouter(
    dependencies=[Security(bearer_scheme)]
)
service = StudentService()


@student_router.get(
    "",
    response_model=SuccessResponse[list[StudentOut]],
    responses=AUTH_COMMON_RESPONSES,
)
def list_students(
        offset: int = 0,
        limit: int = 100,
        db: Session = Depends(get_db),
        _: CurrentUser = Depends(require_current_user),
) -> SuccessResponse[list[StudentOut]]:
    students = service.list_students(db, offset=offset, limit=limit)
    data = [StudentOut.model_validate(student) for student in students]
    return success_response(data=data)


@student_router.get(
    "/{student_id:int}",
    response_model=SuccessResponse[StudentOut],
    responses={
        401: UNAUTHORIZED_401,
        404: NOT_FOUND_404,
        500: INTERNAL_500,
    },
)
def get_student(
        student_id: int,
        db: Session = Depends(get_db),
        _: CurrentUser = Depends(require_current_user),
) -> SuccessResponse[StudentOut]:
    student = service.get_student(db, student_id)
    return success_response(StudentOut.model_validate(student))


@student_router.get(
    "/search",
    response_model=SuccessResponse[list[StudentOut]],
    responses={
        400: BAD_REQUEST_400,
        401: UNAUTHORIZED_401,
        500: INTERNAL_500,
    }
)
def search_students(
        keyword: str | None = None,
        min_age: int | None = None,
        max_age: int | None = None,
        offset: int = 0,
        limit: int = 100,
        db: Session = Depends(get_db),
        _: CurrentUser = Depends(require_current_user),
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
    return success_response(data)


@student_router.post(
    "",
    response_model=SuccessResponse[StudentOut],
    status_code=status.HTTP_201_CREATED,
    responses={
        400: BAD_REQUEST_400,
        401: UNAUTHORIZED_401,
        403: FORBIDDEN_403,
        409: CONFLICT_409,
        500: INTERNAL_500,
    },
)
def create_student(
        data: StudentCreate,
        request: Request,
        response: Response,
        db: Session = Depends(get_db),
        _: CurrentUser = Depends(require_permissions("student:write")),
) -> SuccessResponse[StudentOut]:
    student = service.create_student(db, data)

    # Set Location header
    location = request.url_for("get_student", student_id=student.id)
    response.headers["location"] = str(location)

    return success_response(
        StudentOut.model_validate(student),
        message="Student created",
    )


@student_router.patch(
    "/{student_id}",
    response_model=SuccessResponse[StudentOut],
    responses={
        400: BAD_REQUEST_400,
        401: UNAUTHORIZED_401,
        403: FORBIDDEN_403,
        404: NOT_FOUND_404,
        500: INTERNAL_500,
    }
)
def update_student(
        student_id: int,
        data: StudentUpdate,
        db: Session = Depends(get_db),
        _: CurrentUser = Depends(require_permissions("student:write")),
) -> SuccessResponse[StudentOut]:
    student = service.update_student(db, student_id, data)
    return success_response(
        StudentOut.model_validate(student),
        message="Student updated",
    )


# Double-gate authorization
@student_router.delete(
    "/{student_id}",
    response_model=SuccessResponse[EmptyData],
    responses=AUTHZ_COMMON_RESPONSES,
)
def delete_student(
        student_id: int,
        db: Session = Depends(get_db),
        _: CurrentUser = Depends(require_roles("ADMIN", "HR_MANAGER")),
        __: CurrentUser = Depends(require_permissions("student:delete")),
) -> SuccessResponse[EmptyData]:
    service.delete_student(db, student_id)
    return success_response(EmptyData(), message="Student deleted")
