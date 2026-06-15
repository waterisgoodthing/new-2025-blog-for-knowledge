from datetime import date, datetime, timedelta
from pathlib import Path
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
from app.services.local_music_source import find_local_music_source
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

LOCAL_MUSIC_DIR = Path(__file__).resolve().parents[3] / "public" / "mymusic"
LOCAL_MUSIC_PREFIX = "/mymusic"


def _today_for_music() -> date:
    now_shanghai = datetime.now(ZoneInfo("Asia/Shanghai"))
    if now_shanghai.hour < 8:
        return (now_shanghai - timedelta(days=1)).date()
    return now_shanghai.date()


def _local_music_status():
    return find_local_music_source(
        LOCAL_MUSIC_DIR,
        public_prefix=LOCAL_MUSIC_PREFIX,
        target_date=_today_for_music(),
    )


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
    status = _local_music_status()
    return {
        "api_base_url": "",
        "enabled": status.exists,
        "timeout_seconds": 0,
        "retry_count": 0,
        "source_type": "local_single",
        "source_dir": status.source_dir,
        "selected_file": status.selected_file,
        "warnings": status.warnings,
    }


@router.put("/config")
async def update_config(
    req: NetEaseConfigUpdate,
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(get_passkey_admin),
):
    raise HTTPException(status_code=410, detail="External NetEase configuration is disabled; use public/mymusic as the only music source.")


@router.get("/health")
async def health_check(
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(get_current_admin),
):
    status = _local_music_status()
    return {
        "status": "ok" if status.exists else "missing",
        "source_type": "local_single",
        "source_dir": status.source_dir,
        "selected_file": status.selected_file,
        "warnings": status.warnings,
    }


@router.get("/source-rules")
async def list_source_rules(
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(get_current_admin),
):
    return []


@router.post("/source-rules")
async def create_source_rule(
    req: SourceRuleCreate,
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(get_current_admin),
):
    raise HTTPException(status_code=410, detail="External source rules are disabled; use public/mymusic as the only music source.")


@router.put("/source-rules/{rule_id}")
async def update_source_rule(
    rule_id: int,
    req: SourceRuleUpdate,
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(get_current_admin),
):
    raise HTTPException(status_code=410, detail="External source rules are disabled; use public/mymusic as the only music source.")


@router.delete("/source-rules/{rule_id}")
async def delete_source_rule(
    rule_id: int,
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(get_current_admin),
):
    raise HTTPException(status_code=410, detail="External source rules are disabled; use public/mymusic as the only music source.")


@router.post("/sync")
async def sync_candidates(
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(get_current_admin),
):
    raise HTTPException(status_code=410, detail="External candidate sync is disabled; use public/mymusic as the only music source.")


@router.post("/sync/{rule_id}")
async def sync_rule_candidates(
    rule_id: int,
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(get_current_admin),
):
    raise HTTPException(status_code=410, detail="External candidate sync is disabled; use public/mymusic as the only music source.")


@router.get("/candidates")
async def list_candidates(
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(get_current_admin),
):
    return {
        "items": [],
        "total": 0,
        "page": page,
        "size": size,
    }


@router.get("/daily-song")
async def get_daily_song(
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(get_current_admin),
):
    status = _local_music_status()
    return status.track


@router.post("/generate-song")
async def generate_song(
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(get_current_admin),
):
    status = _local_music_status()
    if not status.track:
        raise HTTPException(status_code=404, detail="No local music file available in public/mymusic")
    return status.track


@router.get("/history")
async def song_history(
    limit: int = Query(30, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(get_current_admin),
):
    return []


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
    status = _local_music_status()
    return status.track


@router.get("/history/public")
async def public_song_history(
    limit: int = Query(30, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    return []


@router.get("/diagnostics")
async def diagnostics(
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(get_current_admin),
):
    today = _today_for_music()
    status = _local_music_status()
    track = status.track

    return {
        "today": today.isoformat(),
        "today_song_exists": track is not None,
        "today_song": {
            "id": track["id"],
            "title": track["title"],
            "artist": track["artist"],
        } if track else None,
        "history_count": 0,
        "candidate_pool_count": status.file_count,
        "netease_configured": False,
        "netease_reachable": False,
        "netease_error": "",
        "last_sync": None,
        "source_type": "local_single",
        "source_dir": status.source_dir,
        "public_prefix": status.public_prefix,
        "local_source_exists": status.exists,
        "local_file_count": status.file_count,
        "selected_file": status.selected_file,
        "warnings": status.warnings,
    }
