from pydantic import BaseModel, EmailStr, Field
from fastapi import APIRouter, Depends, Request, Response, status

from schemas.auth.login_out_schema import LoginResponse
from schemas.auth.login_schema import LoginRequest
from services.auth_service import AuthService, TokenPairOut
from security.providers import get_auth_service
from security.principals import CurrentUser
from security.guards import require_current_user_verified


auth_router = APIRouter(prefix="/api/v1/auth", tags=["Auth"])


def _to_response(out: TokenPairOut) -> LoginResponse:
    if out.expires_in is None:
        raise RuntimeError("TokenPairOut.expires_in must not be None")
    return LoginResponse(
        access_token=out.access_token,
        token_type=out.token_type,
        expires_in=out.expires_in,
    )


@auth_router.post("/login", response_model=LoginResponse)
def login(
        payload: LoginRequest,
        request: Request,
        response: Response,
        svc: AuthService = Depends(get_auth_service),
) -> LoginResponse:
    """
    Login:
    - verify credentials
    - issue access token in body
    - set refresh token cookie (HttpOnly)
    """
    out = svc.login(
        db=request.state.db,  # giả định bạn có DB middleware gắn request.state.db
        request=request,
        response=response,
        email=str(payload.email),
        password=payload.password,
    )
    return _to_response(out)


@auth_router.post(
    "/refresh",
    response_model=TokenPairResponse,
    status_code=status.HTTP_200_OK,
)
def refresh(
    request: Request,
    response: Response,
    svc: AuthService = Depends(get_auth_service),
) -> TokenPairResponse:
    """
    Refresh:
    - read refresh cookie
    - rotate refresh session
    - issue new access token
    - set new refresh cookie
    """
    out = svc.refresh(
        db=request.state.db,
        request=request,
        response=response,
    )
    return _to_response(out)


@auth_router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
)
def logout(
    request: Request,
    response: Response,
    svc: AuthService = Depends(get_auth_service),
) -> Response:
    """
    Logout current device:
    - revoke refresh session (if exists)
    - clear refresh cookie always
    """
    svc.logout(
        db=request.state.db,
        request=request,
        response=response,
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@auth_router.post(
    "/logout-all",
    status_code=status.HTTP_200_OK,
)
def logout_all(
    request: Request,
    response: Response,
    user: CurrentUser = Depends(require_current_user_verified),
    svc: AuthService = Depends(get_auth_service),
) -> dict:
    """
    Logout all devices:
    - require verified current user (token_version valid)
    - revoke all refresh sessions for this user
    - clear refresh cookie
    """
    user_id = int(user.user_id)
    revoked = svc.logout_all(
        db=request.state.db,
        user_id=user_id,
        response=response,
    )
    return {"revoked_sessions": revoked}
