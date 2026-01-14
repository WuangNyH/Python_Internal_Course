from dataclasses import dataclass

from security.principals import CurrentUser


@dataclass(frozen=True)
class RequestContext:
    request_id: str
    trace_id: str | None
    current_user: CurrentUser | None

    ip: str | None = None
    user_agent: str | None = None
    token_error: str | None = None
