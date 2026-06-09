from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.music_daily import (
    DailySong,
    MusicCandidate,
    MusicSourceRule,
    MusicSyncLog,
    NetEaseApiConfig,
)
from app.models.note import User
from app.routers.auth import get_current_admin, get_passkey_admin
from app.services.netease_service import (
    check_health,
    ensure_default_source_rules,
    generate_daily_song,
    get_netease_config,
    get_song_history,
    get_or_create_today_song,
    sync_all_candidates,
    sync_candidates_for_rule,
)

router = APIRouter(prefix="/api/music/manage", tags=["music-manage"])


class NetEaseConfigUpdate(BaseModel):
    api_base_url: str | None = None
    enabled: bool | None = None
    timeout_seconds: int | None = None
    retry_count: int | None = None


class SourceRuleCreate(BaseModel):
    source_type: str
    source_value: str
    enabled: bool = True
    sort_order: int = 0


class SourceRuleUpdate(BaseModel):
    source_type: str | None = None
    source_value: str | None = None
    enabled: bool | None = None
    sort_order: int | None = None


@router.get("/config")
async def get_config(
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(get_current_admin),
):
    config = await get_netease_config(db)
    return {
        "api_base_url": config.api_base_url,
        "enabled": config.enabled,
        "timeout_seconds": config.timeout_seconds,
        "retry_count": config.retry_count,
    }


@router.put("/config")
async def update_config(
    req: NetEaseConfigUpdate,
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(get_passkey_admin),
):
    config = await get_netease_config(db)
    if req.api_base_url is not None:
        config.api_base_url = req.api_base_url
    if req.enabled is not None:
        config.enabled = req.enabled
    if req.timeout_seconds is not None:
        config.timeout_seconds = req.timeout_seconds
    if req.retry_count is not None:
        config.retry_count = req.retry_count
    db.add(config)
    return {"message": "Config updated"}


@router.get("/health")
async def health_check(
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(get_current_admin),
):
    config = await get_netease_config(db)
    return await check_health(config.api_base_url, config.timeout_seconds)


@router.get("/source-rules")
async def list_source_rules(
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(get_current_admin),
):
    rules = await ensure_default_source_rules(db)
    return [
        {
            "id": r.id,
            "source_type": r.source_type,
            "source_value": r.source_value,
            "enabled": r.enabled,
            "sort_order": r.sort_order,
        }
        for r in rules
    ]


@router.post("/source-rules")
async def create_source_rule(
    req: SourceRuleCreate,
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(get_current_admin),
):
    rule = MusicSourceRule(
        source_type=req.source_type,
        source_value=req.source_value,
        enabled=req.enabled,
        sort_order=req.sort_order,
    )
    db.add(rule)
    await db.flush()
    return {"id": rule.id, "source_type": rule.source_type, "source_value": rule.source_value}


@router.put("/source-rules/{rule_id}")
async def update_source_rule(
    rule_id: int,
    req: SourceRuleUpdate,
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(get_current_admin),
):
    result = await db.execute(select(MusicSourceRule).where(MusicSourceRule.id == rule_id))
    rule = result.scalar_one_or_none()
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    if req.source_type is not None:
        rule.source_type = req.source_type
    if req.source_value is not None:
        rule.source_value = req.source_value
    if req.enabled is not None:
        rule.enabled = req.enabled
    if req.sort_order is not None:
        rule.sort_order = req.sort_order
    db.add(rule)
    return {"message": "Rule updated"}


@router.delete("/source-rules/{rule_id}")
async def delete_source_rule(
    rule_id: int,
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(get_current_admin),
):
    result = await db.execute(select(MusicSourceRule).where(MusicSourceRule.id == rule_id))
    rule = result.scalar_one_or_none()
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    await db.delete(rule)
    return {"message": "Rule deleted"}


@router.post("/sync")
async def sync_candidates(
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(get_current_admin),
):
    result = await sync_all_candidates(db)
    return result


@router.post("/sync/{rule_id}")
async def sync_rule_candidates(
    rule_id: int,
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(get_current_admin),
):
    result = await db.execute(select(MusicSourceRule).where(MusicSourceRule.id == rule_id))
    rule = result.scalar_one_or_none()
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    config = await get_netease_config(db)
    count = await sync_candidates_for_rule(db, config, rule)
    return {"synced": count}


@router.get("/candidates")
async def list_candidates(
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(get_current_admin),
):
    count_result = await db.execute(select(MusicCandidate))
    total_query = await db.execute(select(MusicCandidate))
    all_items = list(total_query.scalars().all())
    total = len(all_items)

    result = await db.execute(
        select(MusicCandidate)
        .order_by(MusicCandidate.id.desc())
        .offset((page - 1) * size)
        .limit(size)
    )
    candidates = list(result.scalars().all())
    return {
        "items": [
            {
                "id": c.id,
                "netease_id": c.netease_id,
                "title": c.title,
                "artist": c.artist,
                "album": c.album,
                "artwork_url": c.artwork_url,
                "netease_url": c.netease_url,
                "synced_at": c.synced_at.isoformat() if c.synced_at else None,
            }
            for c in candidates
        ],
        "total": total,
        "page": page,
        "size": size,
    }


@router.get("/daily-song")
async def get_daily_song(
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(get_current_admin),
):
    song = await get_or_create_today_song(db)
    if not song:
        return None
    return {
        "id": song.id,
        "date": song.date.isoformat(),
        "title": song.title,
        "artist": song.artist,
        "album": song.album,
        "artwork_url": song.artwork_url,
        "preview_url": song.preview_url,
        "netease_url": song.netease_url,
        "recommendation_reason": song.recommendation_reason,
    }


@router.post("/generate-song")
async def generate_song(
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(get_current_admin),
):
    now_shanghai = datetime.now(ZoneInfo("Asia/Shanghai"))
    if now_shanghai.hour < 8:
        today = (now_shanghai - timedelta(days=1)).date()
    else:
        today = now_shanghai.date()
    result = await db.execute(select(DailySong).where(DailySong.date == today))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Today's song already exists")
    song = await generate_daily_song(db, today)
    if not song:
        raise HTTPException(status_code=404, detail="No candidates available")
    return {
        "id": song.id,
        "date": song.date.isoformat(),
        "title": song.title,
        "artist": song.artist,
    }


@router.get("/history")
async def song_history(
    limit: int = Query(30, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(get_current_admin),
):
    songs = await get_song_history(db, limit)
    return [
        {
            "id": s.id,
            "date": s.date.isoformat(),
            "title": s.title,
            "artist": s.artist,
            "album": s.album,
            "artwork_url": s.artwork_url,
            "preview_url": s.preview_url,
            "netease_url": s.netease_url,
            "recommendation_reason": s.recommendation_reason,
        }
        for s in songs
    ]


@router.get("/sync-logs")
async def list_sync_logs(
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(get_current_admin),
):
    result = await db.execute(
        select(MusicSyncLog).order_by(MusicSyncLog.created_at.desc()).limit(limit)
    )
    logs = list(result.scalars().all())
    return [
        {
            "id": l.id,
            "action": l.action,
            "status": l.status,
            "candidates_found": l.candidates_found,
            "error_message": l.error_message,
            "created_at": l.created_at.isoformat() if l.created_at else None,
        }
        for l in logs
    ]


@router.get("/daily-song/public")
async def get_public_daily_song(db: AsyncSession = Depends(get_db)):
    song = await get_or_create_today_song(db)
    if not song:
        return None
    return {
        "id": song.id,
        "date": song.date.isoformat(),
        "title": song.title,
        "artist": song.artist,
        "album": song.album,
        "artwork_url": song.artwork_url,
        "preview_url": song.preview_url,
        "netease_url": song.netease_url,
        "recommendation_reason": song.recommendation_reason,
    }


@router.get("/history/public")
async def public_song_history(
    limit: int = Query(30, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    songs = await get_song_history(db, limit)
    return [
        {
            "id": s.id,
            "date": s.date.isoformat(),
            "title": s.title,
            "artist": s.artist,
            "album": s.album,
            "artwork_url": s.artwork_url,
            "preview_url": s.preview_url,
            "netease_url": s.netease_url,
        }
        for s in songs
    ]
