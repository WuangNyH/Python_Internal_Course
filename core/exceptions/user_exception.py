import uuid

from core.exceptions.base import BusinessException


class UserNotFoundException(BusinessException):
    def __init__(self, *, user_id: uuid.UUID | None = None):
        super().__init__(
            error_code="USER_NOT_FOUND",
            message="User not found",
            status_code=404,
            extra={"user_id": str(user_id)} if user_id is not None else None,
        )


class UserEmailAlreadyExistsException(BusinessException):
    def __init__(self, *, email: str):
        super().__init__(
            error_code="USER_EMAIL_EXISTS",
            message="Email already exists",
            status_code=409,
            extra={"email": email},
        )


class UserInactiveException(BusinessException):
    def __init__(self, *, user_id: uuid.UUID | None):
        super().__init__(
            error_code="USER_INACTIVE",
            message="User is inactive",
            status_code=403,
            extra={"user_id": str(user_id)} if user_id is not None else None,
        )


class UserDeleteSelfForbiddenException(BusinessException):
    def __init__(self, *, user_id: uuid.UUID | None):
        super().__init__(
            error_code="USER_DELETE_SELF_FORBIDDEN",
            message="User cannot delete itself",
            status_code=403,
            extra={"user_id": str(user_id)} if user_id is not None else None,
        )


class UserUpdateForbiddenException(BusinessException):
    def __init__(self, *, user_id: uuid.UUID | None):
        super().__init__(
            error_code="USER_UPDATE_FORBIDDEN",
            message="User update is forbidden",
            status_code=403,
            extra={"user_id": str(user_id)} if user_id is not None else None,
        )


class UserUpdateSelfForbiddenException(BusinessException):
    def __init__(self, *, user_id: uuid.UUID | None):
        super().__init__(
            error_code="USER_UPDATE_SELF_FORBIDDEN",
            message="User cannot update itself",
            status_code=403,
            extra={"user_id": str(user_id)} if user_id is not None else None,
        )
