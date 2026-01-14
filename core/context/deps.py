from fastapi import Request

from core.context.request_context import RequestContext
from core.http.request_state_keys import RequestStateKeys
from security.dependencies import get_token_claims, get_token_error
from security.principals import CurrentUser


def get_request_context(request: Request) -> RequestContext:
    """
    Cross-cutting RequestContext:
    - request_id: request.state.request_id (RequestIdMiddleware)
    - trace_id: request.state.trace_id (TraceIdMiddleware)
    - token_claims/token_error: TokenContextMiddleware
    - current_user: optional (không raise)
    """
    request_id = getattr(request.state, RequestStateKeys.REQUEST_ID, None)
    if not request_id:
        raise RuntimeError("request_id is missing in request.state (RequestIdMiddleware not installed)")

    trace_id = getattr(request.state, RequestStateKeys.TRACE_ID, None)

    token_error = get_token_error(request)
    claims = get_token_claims(request)

    current_user: CurrentUser | None = None
    if claims and not token_error:
        # Optional build principal from claims (không raise)
        current_user = CurrentUser.from_claims(claims)

    ip = getattr(request.client, "host", None) if request.client else None
    user_agent = request.headers.get("User-Agent")

    return RequestContext(
        request_id=request_id,
        trace_id=trace_id,
        current_user=current_user,
        ip=ip,
        user_agent=user_agent,
        token_error=token_error,
    )
