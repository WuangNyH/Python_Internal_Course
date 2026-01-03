import secrets
import hashlib

def generate_refresh_token() -> str:
    # 43~86 chars: đủ mạnh
    return secrets.token_urlsafe(64)

def hash_refresh_token(token: str) -> str:
    # DB chỉ lưu hash (che dấu token)
    return hashlib.sha256(token.encode("utf-8")).hexdigest()
