import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import Any, Mapping


def to_json_safe(value: Any) -> Any:
    """
    Convert common Python/SQLAlchemy values to JSON-serializable structures.
    Keep it conservative and stable for logging/audit usage.

    Design principles (enterprise logging):
    - Best-effort: never raise
    - Stable: deterministic output
    - Generic: not coupled to any specific domain model
    """
    if value is None:
        return None

    # primitives
    if isinstance(value, (str, int, float, bool)):
        return value

    # uuid / datetime / date / decimal
    if isinstance(value, uuid.UUID):
        return str(value)
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, Decimal):
        return str(value)

    # mappings
    if isinstance(value, Mapping):
        return {str(k): to_json_safe(v) for k, v in value.items()}

    # iterables (but not str, already handled above)
    if isinstance(value, (list, tuple, set)):
        return [to_json_safe(v) for v in value]

    # pydantic v2 models
    if hasattr(value, "model_dump"):
        try:
            dumped = value.model_dump()
            return to_json_safe(dumped)
        except (TypeError, ValueError):
            return str(value)

    # fallback (ORM objects, enums, unknown types, ...)
    return str(value)
