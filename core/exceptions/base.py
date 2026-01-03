class BusinessException(Exception):
    """
    Base class for entire business exception
    """

    def __init__(
        self,
        *,
        message: str,
        error_code: str,
        status_code: int = 400,
        extra: dict | None = None,
    ):
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        self.extra = extra or {}
        super().__init__(message)
