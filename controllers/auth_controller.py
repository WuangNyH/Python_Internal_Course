from fastapi import APIRouter, Depends, Request, Response, status
from fastapi.params import Security
from sqlalchemy.orm import Session

from core.openapi_responses import INTERNAL_500, AUTH_COMMON_RESPONSES
from core.responses import success_response
from dependencies.db import get_db
from schemas.auth.login_out_schema import LoginResponse
from schemas.auth.login_schema import LoginRequest
from schemas.auth.logout_out_schema import LogoutAllResult
from schemas.response.base import SuccessResponse
from security.schemes import bearer_scheme
from services.auth_service import AuthService, TokenPairOut
from security.providers import get_auth_service
from security.principals import CurrentUser
from security.guards import require_current_user_verified

auth_router = APIRouter()


def _to_response(out: TokenPairOut) -> SuccessResponse[LoginResponse]:
    if out.expires_in is None:
        raise RuntimeError("TokenPairOut.expires_in must not be None")
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
        svc: AuthService = Depends(get_auth_service),
        db: Session = Depends(get_db)
) -> SuccessResponse[LoginResponse]:
    """
    Login:
    - verify credentials
    - issue access token in body
    - set refresh token cookie (HttpOnly)
    """
    out = svc.login(
        db=db,
        request=request,
        response=response,
        email=str(payload.email),
        password=payload.password,
    )
    return _to_response(out)


@auth_router.post(
    "/refresh",
    response_model=SuccessResponse[LoginResponse],
    responses=AUTH_COMMON_RESPONSES,
)
def refresh(
        request: Request,
        response: Response,
        svc: AuthService = Depends(get_auth_service),
        db: Session = Depends(get_db),
) -> SuccessResponse[LoginResponse]:
    """
    Refresh:
    - read refresh cookie
    - rotate refresh session
    - issue new access token
    - set new refresh cookie
    """
    out = svc.refresh(
        db=db,
        request=request,
        response=response,
    )
    return _to_response(out)


@auth_router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={500: INTERNAL_500},
)
def logout(
        request: Request,
        response: Response,
        svc: AuthService = Depends(get_auth_service),
        db: Session = Depends(get_db),
) -> Response:
    """
    Logout current device:
    - revoke refresh session (if exists)
    - clear refresh cookie always
    """
    svc.logout(
        db=db,
        request=request,
        response=response,
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@auth_router.post(
    "/logout-all",
    dependencies=[Security(bearer_scheme)],
    response_model=SuccessResponse[LogoutAllResult],
    responses=AUTH_COMMON_RESPONSES,
)
def logout_all(
        response: Response,
        user: CurrentUser = Depends(require_current_user_verified),
        svc: AuthService = Depends(get_auth_service),
        db: Session = Depends(get_db),
) -> SuccessResponse[LogoutAllResult]:
    """
    Logout all devices:
    - require verified current user (token_version valid)
    - revoke all refresh sessions for this user
    - clear refresh cookie
    """
    user_id = int(user.user_id)
    revoked = svc.logout_all(
        db=db,
        user_id=user_id,
        response=response,
    )
    return success_response(LogoutAllResult(revoked_sessions=revoked))
