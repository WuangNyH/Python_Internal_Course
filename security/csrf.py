from urllib.parse import urlparse
from fastapi import Request

from configs.env import settings_config
from core.exceptions.csrf_exceptions import CsrfMissingOriginException, CsrfOriginRejectedException


def _normalize_origin(value: str) -> str | None:
    """
    Normalize an origin string to "scheme://host[:port]" (no path).
    """
    v = (value or "").strip()
    if not v:
        return None

    parsed = urlparse(v)
    if parsed.scheme and parsed.netloc:
        # input is full URL or origin-like
        return f"{parsed.scheme}://{parsed.netloc}"

    # Some clients may send already origin-like without parsing as URL
    if "://" in v and "/" not in v.replace("://", "", 1):
        return v

    return None


def _origin_from_referer(referer: str) -> str | None:
    """
    Extract origin from referer URL.
    """
    ref = (referer or "").strip()
    if not ref:
        return None
    parsed = urlparse(ref)
    if not parsed.scheme or not parsed.netloc:
        return None
    return f"{parsed.scheme}://{parsed.netloc}"


def _is_allowed(origin: str, allowlist: list[str]) -> bool:
    # exact match is the safest
    return origin in allowlist


def require_allowed_origin_or_referer(request: Request) -> None:
    """
    CSRF defense for cookie-based auth endpoints (refresh/logout).

    Rule:
    - If Origin header exists => must be in allowlist
    - Else if Referer exists => referer origin must be in allowlist
    - Else => 403

    Allowlist source: settings.security.cors.allow_origins
    """
    settings = settings_config()
    csrf_settings = settings.security.csrf

    # If CSRF defense disabled explicitly
    if not csrf_settings.enabled:
        return

    # Prefer CSRF allowlist; fallback to CORS allowlist for backward compatibility
    csrf_allowlist = list(csrf_settings.trusted_origins or [])
    if not csrf_allowlist:
        # fail-closed: must set CSRF_TRUSTED_ORIGINS in .env
        raise CsrfMissingOriginException(allowed=[])

    origin_raw = request.headers.get("Origin")
    referer_raw = request.headers.get("Referer")

    origin = _normalize_origin(origin_raw) if origin_raw else None
    if origin:
        if _is_allowed(origin, csrf_allowlist):
            return
        raise CsrfOriginRejectedException(origin=origin_raw, referer=referer_raw, allowed=csrf_allowlist)

    # fallback referer
    referer_origin = _origin_from_referer(referer_raw) if referer_raw else None
    if referer_origin:
        if _is_allowed(referer_origin, csrf_allowlist):
            return
        raise CsrfOriginRejectedException(origin=origin_raw, referer=referer_raw, allowed=csrf_allowlist)

    # Missing both Origin and Referer
    raise CsrfMissingOriginException(allowed=csrf_allowlist)
