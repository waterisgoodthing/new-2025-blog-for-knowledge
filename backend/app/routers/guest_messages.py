from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.guest_message import GuestMessage, GuestMessageBan
from app.models.note import User
from app.routers.auth import get_current_admin, get_optional_user
from app.schemas.guest_message import (
    GuestMessageCreate,
    GuestMessageListResponse,
    GuestMessageModerate,
    GuestMessageOut,
)

router = APIRouter(prefix="/api/guest-messages", tags=["guest-messages"])

RATE_LIMIT_WINDOW_SECONDS = 60
RATE_LIMIT_MAX_MESSAGES = 5
BAN_HOURS = 24


def _get_client_ip(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


async def _check_rate_limit(db: AsyncSession, ip: str) -> None:
    window_start = datetime.now(timezone.utc) - timedelta(seconds=RATE_LIMIT_WINDOW_SECONDS)
    count_result = await db.execute(
        select(func.count())
        .select_from(GuestMessage)
        .where(GuestMessage.ip_address == ip)
        .where(GuestMessage.created_at >= window_start)
    )
    count = count_result.scalar() or 0
    if count >= RATE_LIMIT_MAX_MESSAGES:
        ban_until = datetime.now(timezone.utc) + timedelta(hours=BAN_HOURS)
        ban = GuestMessageBan(
            ip_address=ip,
            reason=f"Rate limit exceeded: {count} messages in {RATE_LIMIT_WINDOW_SECONDS}s",
            expires_at=ban_until,
        )
        db.add(ban)
        await db.flush()
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="发送过于频繁，请稍后再试",
        )


async def _check_ban(db: AsyncSession, ip: str) -> None:
    now = datetime.now(timezone.utc)
    ban_result = await db.execute(
        select(GuestMessageBan)
        .where(GuestMessageBan.ip_address == ip)
        .where(
            (GuestMessageBan.expires_at.is_(None)) | (GuestMessageBan.expires_at > now)
        )
        .order_by(GuestMessageBan.created_at.desc())
        .limit(1)
    )
    ban = ban_result.scalar_one_or_none()
    if ban is not None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="您已被暂时限制发言，请稍后再试",
        )


@router.post("", response_model=GuestMessageOut, status_code=status.HTTP_201_CREATED)
async def create_guest_message(
    req: GuestMessageCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    ip = _get_client_ip(request)
    ua = request.headers.get("user-agent", "")

    await _check_ban(db, ip)
    await _check_rate_limit(db, ip)

    message = GuestMessage(
        content=req.content.strip(),
        nickname=req.nickname.strip() if req.nickname else None,
        attachment_type=req.attachment_type,
        attachment_slug=req.attachment_slug,
        ip_address=ip,
        user_agent=ua,
        status="visible",
    )
    db.add(message)
    await db.flush()
    await db.refresh(message)
    return message


@router.get("", response_model=GuestMessageListResponse)
async def list_guest_messages(
    attachment_type: Optional[str] = None,
    attachment_slug: Optional[str] = None,
    status_filter: Optional[str] = Query(None, alias="status", pattern="^(visible|hidden|deleted)$"),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user),
):
    is_admin = current_user is not None and getattr(current_user, "is_admin", False)

    query = select(GuestMessage)
    if is_admin and status_filter:
        query = query.where(GuestMessage.status == status_filter)
    elif not is_admin:
        query = query.where(GuestMessage.status == "visible")

    if attachment_type:
        query = query.where(GuestMessage.attachment_type == attachment_type)
    if attachment_slug:
        query = query.where(GuestMessage.attachment_slug == attachment_slug)

    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar() or 0

    query = query.order_by(GuestMessage.created_at.desc()).offset((page - 1) * size).limit(size)
    result = await db.execute(query)
    messages = result.scalars().all()

    return GuestMessageListResponse(items=messages, total=total, page=page, size=size)


@router.put("/{message_id}/moderate", response_model=GuestMessageOut)
async def moderate_guest_message(
    message_id: str,
    req: GuestMessageModerate,
    db: AsyncSession = Depends(get_db),
    _admin=Depends(get_current_admin),
):
    import uuid as _uuid
    try:
        mid = _uuid.UUID(message_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid message ID")

    result = await db.execute(select(GuestMessage).where(GuestMessage.id == mid))
    message = result.scalar_one_or_none()
    if message is None:
        raise HTTPException(status_code=404, detail="Message not found")

    message.status = req.status
    await db.flush()
    await db.refresh(message)
    return message


@router.get("/bans")
async def list_bans(
    db: AsyncSession = Depends(get_db),
    _admin=Depends(get_current_admin),
):
    now = datetime.now(timezone.utc)
    result = await db.execute(
        select(GuestMessageBan)
        .where(
            (GuestMessageBan.expires_at.is_(None)) | (GuestMessageBan.expires_at > now)
        )
        .order_by(GuestMessageBan.created_at.desc())
    )
    bans = result.scalars().all()
    return [
        {
            "id": b.id,
            "ip_address": b.ip_address,
            "reason": b.reason,
            "expires_at": b.expires_at,
            "created_at": b.created_at,
        }
        for b in bans
    ]
