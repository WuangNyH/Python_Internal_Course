from datetime import datetime
from pydantic import BaseModel, Field


class EmptyData(BaseModel):
    pass


class HealthResponse(BaseModel):
    status: str = Field(..., examples=["ok"])
    timestamp: datetime
    request_id: str | None = None
    trace_id: str | None = None