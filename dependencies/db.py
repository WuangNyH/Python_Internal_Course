from fastapi import Request
from sqlalchemy.orm import Session


def get_db(request: Request) -> Session:
    db = getattr(request.state, "db", None)
    if db is None:
        raise RuntimeError("DB session is not available on request.state. Check DBSessionMiddleware order.")
    return db
