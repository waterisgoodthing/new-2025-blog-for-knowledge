from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse

from app.models.note import User
from app.routers.auth import get_current_user
from app.schemas.ai_polish import PolishRequest
from app.services.ai_polish_service import polish_stream
from app.utils.rate_limit import RateLimiter

router = APIRouter(prefix="/api/ai", tags=["ai"])

_rate_limiter = RateLimiter(max_requests=10, window_seconds=60)


@router.post("/polish")
async def polish(
    req: PolishRequest,
    request: Request,
    user: User = Depends(get_current_user),
):
    _rate_limiter.check(str(user.id))

    return StreamingResponse(
        polish_stream(
            text=req.text,
            action=req.action.value,
            context=req.context,
            request=request,
            title=req.title,
            note_type=req.note_type,
            existing_tags=req.existing_tags,
        ),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
