from datetime import datetime, timezone


def utcnow() -> datetime:
    """
    Return timezone-aware UTC datetime.

    Always use this function instead of datetime.utcnow()
    or datetime.now(timezone.utc) directly.
    """
    return datetime.now(timezone.utc)
