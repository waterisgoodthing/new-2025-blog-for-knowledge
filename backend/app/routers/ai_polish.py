from fastapi import APIRouter, Cookie, Depends, Request
from fastapi.responses import StreamingResponse

from app.database import get_db
from app.models.note import User
from app.routers.auth import get_current_admin
from app.schemas.ai_polish import PolishRequest
from app.services.ai_polish_service import polish_stream
from app.utils.rate_limit import RateLimiter
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/api/ai", tags=["ai"])

_rate_limiter = RateLimiter(max_requests=10, window_seconds=60)


@router.post("/polish")
async def polish(
    req: PolishRequest,
    request: Request,
    user: User = Depends(get_current_admin),
    session_token: str | None = Cookie(None, alias="admin_session"),
    db: AsyncSession = Depends(get_db),
):
    _rate_limiter.check(str(user.id))

    from app.services.audit_service import audit_action
    await audit_action(
        db, action="ai_call", session_token=session_token, request=request,
        entity_type="ai_polish", after={"action": req.action.value, "text_length": len(req.text)},
    )

    return StreamingResponse(
        polish_stream(
            text=req.text,
            action=req.action.value,
            context=req.context,
            request=request,
            title=req.title,
            note_type=req.note_type,
            existing_tags=req.existing_tags,
            custom_prompt=req.custom_prompt,
        ),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
