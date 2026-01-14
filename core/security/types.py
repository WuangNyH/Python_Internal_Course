from enum import StrEnum

class TokenError(StrEnum):
    EXPIRED = "expired"
    INVALID = "invalid"


class TokenType(StrEnum):
    ACCESS = "access"
    REFRESH = "refresh"
    UNKNOWN = "unknown"