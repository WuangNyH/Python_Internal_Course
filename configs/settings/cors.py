from pydantic import BaseModel, ConfigDict, Field


class CorsSettings(BaseModel):
    """
    CORS settings (enterprise):
    - allow_origins: whitelist origin của SPA, KHÔNG dùng '*'
    - allow_credentials=True để browser gửi cookie (refresh token)
    - expose_headers: để FE đọc X-Trace-Id
    """
    model_config = ConfigDict(frozen=True)

    enabled: bool = Field(default=True)

    # môi trường prod: ["https://app.company.com"]
    # dev: ["http://localhost:5173", "http://localhost:3000"]
    allow_origins: list[str] = Field(default_factory=list)

    allow_methods: list[str] = Field(default_factory=lambda: [
        "GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"
    ])

    # Header FE gửi:
    # - Authorization (access token)
    # - Content-Type
    allow_headers: list[str] = Field(default_factory=lambda: [
        "Authorization", "Content-Type"
    ])

    # Header FE cần đọc:
    expose_headers: list[str] = Field(default_factory=lambda: [
        "X-Trace-Id"
    ])

    allow_credentials: bool = Field(default=True)

    # Cache preflight 10 phút
    max_age: int = Field(default=600)
