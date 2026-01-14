from passlib.context import CryptContext

_pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


def hash_password(plain_password: str) -> str:
    if not plain_password or plain_password.strip() == "":
        raise ValueError(">>>>> Password must not be empty")  # Tầng service sẽ xử lý
    return _pwd_context.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    if not plain_password or not hashed_password:
        return False
    return _pwd_context.verify(plain_password, hashed_password)


def needs_rehash(hashed_password: str) -> bool:
    if not hashed_password:
        return False
    return _pwd_context.needs_update(hashed_password)
