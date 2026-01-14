from fastapi import APIRouter, Depends, Request, Response
from fastapi.params import Security
from sqlalchemy.orm import Session

from core.context.deps import get_request_context
from core.context.request_context import RequestContext
from core.openapi_responses import AUTH_COMMON_RESPONSES, AUTHZ_COMMON_RESPONSES
from core.responses import success_response
from dependencies.db import get_db
from schemas.auth.login_out_schema import LoginResponse
from schemas.auth.login_schema import LoginRequest
from schemas.auth.logout_out_schema import LogoutAllResult
from schemas.common import EmptyData
from schemas.response.base import SuccessResponse
from security.csrf import require_allowed_origin_or_referer
from security.schemes import bearer_scheme
from services.auth_service import AuthService, TokenPairOut
from security.providers import get_auth_service
from security.principals import CurrentUser
from security.guards import require_current_user_verified

auth_router = APIRouter()


def _to_response(out: TokenPairOut) -> SuccessResponse[LoginResponse]:
    return success_response(
        LoginResponse(
            access_token=out.access_token,
            token_type=out.token_type,
            expires_in=out.expires_in,
        )
    )


@auth_router.post(
    "/login",
    response_model=SuccessResponse[LoginResponse],
    responses=AUTH_COMMON_RESPONSES,
)
def login(
        payload: LoginRequest,
        request: Request,
        response: Response,
        db: Session = Depends(get_db),
        ctx: RequestContext = Depends(get_request_context),
        svc: AuthService = Depends(get_auth_service),
) -> SuccessResponse[LoginResponse]:
    """
    Login:
    - verify credentials
    - issue access token in body
    - set refresh token cookie (HttpOnly)
    """
    out = svc.login(
        db=db,
        ctx=ctx,
        request=request,
        response=response,
        email=str(payload.email),
        password=payload.password,
    )
    return _to_response(out)


@auth_router.post(
    "/refresh",
    response_model=SuccessResponse[LoginResponse],
    responses=AUTHZ_COMMON_RESPONSES,
)
def refresh(
        request: Request,
        response: Response,
        db: Session = Depends(get_db),
        ctx: RequestContext = Depends(get_request_context),
        _: None = Depends(require_allowed_origin_or_referer), # CSRF defense
        svc: AuthService = Depends(get_auth_service),
) -> SuccessResponse[LoginResponse]:
    """
    Refresh:
    - read refresh cookie
    - rotate refresh session
    - issue new access token
    - set new refresh cookie (HttpOnly)
    """
    out = svc.refresh(
        db=db,
        ctx=ctx,
        request=request,
        response=response,
    )
    return _to_response(out)


@auth_router.post(
    "/logout",
    response_model=SuccessResponse[EmptyData],
    responses=AUTHZ_COMMON_RESPONSES,
)
def logout(
        request: Request,
        response: Response,
        db: Session = Depends(get_db),
        ctx: RequestContext = Depends(get_request_context),
        _: None = Depends(require_allowed_origin_or_referer), # CSRF defense
        svc: AuthService = Depends(get_auth_service),
) -> SuccessResponse[EmptyData]:
    """
    Logout current device:
    - revoke refresh session (if exists)
    - clear refresh cookie always
    """
    svc.logout(
        db=db,
        ctx=ctx,
        request=request,
        response=response,
    )
    return success_response(EmptyData(), message="Logged out")


@auth_router.post(
    "/logout-all",
    dependencies=[Security(bearer_scheme)],
    response_model=SuccessResponse[LogoutAllResult],
    responses=AUTH_COMMON_RESPONSES,
)
def logout_all(
        response: Response,
        db: Session = Depends(get_db),
        ctx: RequestContext = Depends(get_request_context),
        user: CurrentUser = Depends(require_current_user_verified),
        svc: AuthService = Depends(get_auth_service),
) -> SuccessResponse[LogoutAllResult]:
    """
    Logout all devices:
    - require verified current user (token_version valid)
    - revoke all refresh sessions for this user
    - clear refresh cookie
    """
    user_id = user.user_id
    revoked = svc.logout_all(
        db=db,
        ctx=ctx,
        user_id=user_id,
        response=response,
    )
    return success_response(LogoutAllResult(revoked_sessions=revoked))
