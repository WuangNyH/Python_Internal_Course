from enum import StrEnum


class AuditMode(StrEnum):
    """
    Audit mode controlled by env.

    - off: disable all audit writes
    - security_only: only write security-critical actions
    - on: write all actions
    """
    OFF = "off"
    SECURITY_ONLY = "security_only"
    ON = "on"
