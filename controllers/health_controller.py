from fastapi import APIRouter, Depends
from core.context.deps import get_request_context
from core.context.request_context import RequestContext
from core.utils.datetime_utils import utcnow
from schemas.common import HealthResponse

health_router = APIRouter()


@health_router.get("/health", response_model=HealthResponse)
def health(ctx: RequestContext = Depends(get_request_context)) -> HealthResponse:
    return HealthResponse(
        status="ok",
        timestamp=utcnow(),
        request_id=ctx.request_id,
        trace_id=ctx.trace_id,
    )
