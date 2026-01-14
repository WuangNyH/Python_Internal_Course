import uuid
from fastapi import APIRouter, Depends, status, Security
from fastapi.params import Query
from sqlalchemy.orm import Session

from core.context.deps import get_request_context
from core.context.request_context import RequestContext
from core.openapi_responses import UNAUTHORIZED_401, NOT_FOUND_404, INTERNAL_500, \
    BAD_REQUEST_400, FORBIDDEN_403, CONFLICT_409
from core.responses import success_response
from core.security.permissions import Permissions
from core.security.roles import Roles
from dependencies.db import get_db
from dependencies.providers import get_user_service
from schemas.common import EmptyData
from schemas.request.user_schema import UserCreate, UserSearchParams, UserUpdate
from schemas.response.base import SuccessResponse
from schemas.response.user_out_schema import UserOut, UserListOut
from security.guards import require_permissions, require_roles
from security.principals import CurrentUser
from security.schemes import bearer_scheme
from services.user_service import UserService

user_router = APIRouter(
    dependencies=[Security(bearer_scheme)]
)


@user_router.get(
    "",
    response_model=SuccessResponse[UserListOut],
    responses={
        400: BAD_REQUEST_400,
        401: UNAUTHORIZED_401,
        403: FORBIDDEN_403,
        500: INTERNAL_500,
    },
)
def search_users(
        params: UserSearchParams = Depends(),
        db: Session = Depends(get_db),
        svc: UserService = Depends(get_user_service),
        _: CurrentUser = Depends(require_permissions(Permissions.USER_READ)),
) -> SuccessResponse[UserListOut]:
    """Search users with paging/sort (alive-only)"""
    items, total, meta = svc.search_users(db, params=params)

    data = UserListOut(
        items=[UserOut.model_validate(u) for u in items],
        total=total,
        page=getattr(meta, "page", getattr(params, "page", 1)),
        page_size=getattr(meta, "page_size", getattr(params, "page_size", 20)),
    )
    return success_response(data)


@user_router.get(
    "/{user_id}",
    response_model=SuccessResponse[UserOut],
    responses={
        401: UNAUTHORIZED_401,
        403: FORBIDDEN_403,
        404: NOT_FOUND_404,
        500: INTERNAL_500,
    },
)
def get_user_detail(
        user_id: uuid.UUID,
        db: Session = Depends(get_db),
        svc: UserService = Depends(get_user_service),
        _: CurrentUser = Depends(require_permissions(Permissions.USER_READ)),
) -> SuccessResponse[UserOut]:
    """Get active user by id."""
    u = svc.get_user_or_404(db, user_id=user_id)
    return success_response(UserOut.model_validate(u))


@user_router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=SuccessResponse[UserOut],
    responses={
        400: BAD_REQUEST_400,
        401: UNAUTHORIZED_401,
        403: FORBIDDEN_403,
        409: CONFLICT_409,
        500: INTERNAL_500,
    },
)
def create_user(
        data: UserCreate,
        ctx: RequestContext = Depends(get_request_context),
        db: Session = Depends(get_db),
        svc: UserService = Depends(get_user_service),
        _: CurrentUser = Depends(require_roles(Roles.ADMIN, Roles.HR_MANAGER)),
        __: CurrentUser = Depends(require_permissions(Permissions.USER_WRITE)),
) -> SuccessResponse[UserOut]:
    """Create user (audited logging)"""
    created = svc.create_user(db, data=data, ctx=ctx)
    return success_response(
        UserOut.model_validate(created),
        message="User created",
    )


@user_router.patch(
    "/{user_id}",
    response_model=SuccessResponse[UserOut],
    responses={
        400: BAD_REQUEST_400,
        401: UNAUTHORIZED_401,
        403: FORBIDDEN_403,
        404: NOT_FOUND_404,
        409: CONFLICT_409,
        500: INTERNAL_500,
    },
)
def update_user(
        user_id: uuid.UUID,
        data: UserUpdate,
        ctx: RequestContext = Depends(get_request_context),
        db: Session = Depends(get_db),
        svc: UserService = Depends(get_user_service),
        _: CurrentUser = Depends(require_roles(Roles.ADMIN, Roles.HR_MANAGER)),
        __: CurrentUser = Depends(require_permissions(Permissions.USER_WRITE)),
        forbid_self_update: bool = Query(default=False),
) -> SuccessResponse[UserOut]:
    """Update user (audited logging)"""
    updated = svc.update_user(
        db,
        user_id=user_id,
        data=data,
        ctx=ctx,
        forbid_self_update=forbid_self_update,
    )
    return success_response(
        UserOut.model_validate(updated),
        message="User updated",
    )


@user_router.delete(
    "/{user_id}",
    response_model=SuccessResponse[EmptyData],
    responses={
        400: BAD_REQUEST_400,
        401: UNAUTHORIZED_401,
        403: FORBIDDEN_403,
        404: NOT_FOUND_404,
        409: CONFLICT_409,
        500: INTERNAL_500,
    },
)
def delete_user(
        user_id: uuid.UUID,
        ctx: RequestContext = Depends(get_request_context),
        db: Session = Depends(get_db),
        svc: UserService = Depends(get_user_service),
        _: CurrentUser = Depends(require_roles(Roles.ADMIN)),
        __: CurrentUser = Depends(require_permissions(Permissions.USER_DELETE)),
        hard_delete: bool = Query(default=False),
) -> SuccessResponse[EmptyData]:
    """Delete user (soft/hard) with audited logging"""
    svc.delete_user(
        db,
        user_id=user_id,
        ctx=ctx,
        hard_delete=hard_delete,
    )
    return success_response(EmptyData(), message="User deleted")
