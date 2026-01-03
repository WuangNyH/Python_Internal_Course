from schemas.response.base import ErrorResponse


BAD_REQUEST_400 = {
    "model": ErrorResponse,
    "description": "Invalid parameters (business rule violation)",
}
UNAUTHORIZED_401 = {
    "model": ErrorResponse,
    "description": "Unauthorized (missing/invalid/expired token, or invalid credentials)",
}
FORBIDDEN_403 = {
    "model": ErrorResponse,
    "description": "Forbidden (permission denied)",
}
NOT_FOUND_404 = {
    "model": ErrorResponse,
    "description": "Resource not found",
}
CONFLICT_409 = {
    "model": ErrorResponse,
    "description": "Resource conflict (already exists or unique constraint violation)",
}
INTERNAL_500 = {
    "model": ErrorResponse,
    "description": "Internal server error",
}

AUTH_COMMON_RESPONSES = {
    401: UNAUTHORIZED_401,
    500: INTERNAL_500,
}

AUTHZ_COMMON_RESPONSES = {
    401: UNAUTHORIZED_401,
    403: FORBIDDEN_403,
    500: INTERNAL_500,
}
