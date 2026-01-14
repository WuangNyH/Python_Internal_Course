from fastapi import Request
from sqlalchemy.orm import Session

from core.http.request_state_keys import RequestStateKeys


def get_db(request: Request) -> Session:
    db = getattr(request.state, RequestStateKeys.DB, None)
    if db is None:
        raise RuntimeError("DB session is not available on request.state. Check DBSessionMiddleware order.")
    return db
