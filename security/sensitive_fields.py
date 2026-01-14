from typing import Final, Set

MASK_ALL = "***"

# ===== Sensitive field names (payload, model, request body) =====
SENSITIVE_FIELDS: Final[Set[str]] = {
    # credentials
    "password",
    "hashed_password",
    "current_password",
    "new_password",
    "confirm_password",

    # tokens/secrets
    "access_token",
    "refresh_token",
    "token",
    "jwt",

    "secret",
    "api_key",

    # common auth payload keys
    "authorization",
}
