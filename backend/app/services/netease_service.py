import asyncio
import logging
import random
from datetime import date, datetime, timedelta, timezone
from typing import Any

import httpx
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.music_daily import (
    DailySong,
    MusicCandidate,
    MusicSourceRule,
    MusicSyncLog,
    NetEaseApiConfig,
)

logger = logging.getLogger(__name__)

DEFAULT_SOURCE_RULES = [
    {"source_type": "artist", "source_value": "孙燕姿", "sort_order": 1},
    {"source_type": "artist", "source_value": "陈奕迅", "sort_order": 2},
    {"source_type": "artist", "source_value": "周杰伦", "sort_order": 3},
    {"source_type": "artist", "source_value": "陶喆", "sort_order": 4},
    {"source_type": "artist", "source_value": "西二", "sort_order": 5},
    {"source_type": "search", "source_value": "2000s 华语抒情", "sort_order": 6},
    {"source_type": "search", "source_value": "校园怀旧经典", "sort_order": 7},
    {"source_type": "search", "source_value": "粤语经典", "sort_order": 8},
    {"source_type": "search", "source_value": "民谣", "sort_order": 9},
    {"source_type": "search", "source_value": "英文摇滚经典", "sort_order": 10},
    {"source_type": "search", "source_value": "游戏音乐", "sort_order": 11},
]

ARTIST_WEIGHTS = {
    "孙燕姿": 3.0,
}


async def get_netease_config(db: AsyncSession) -> NetEaseApiConfig:
    result = await db.execute(select(NetEaseApiConfig).limit(1))
    config = result.scalar_one_or_none()
    if not config:
        config = NetEaseApiConfig(api_base_url="http://localhost:3000")
        db.add(config)
        await db.flush()
    return config


async def ensure_default_source_rules(db: AsyncSession) -> list[MusicSourceRule]:
    result = await db.execute(select(MusicSourceRule))
    existing = list(result.scalars().all())
    if existing:
        return existing

    rules = []
    for rule_data in DEFAULT_SOURCE_RULES:
        rule = MusicSourceRule(**rule_data)
        db.add(rule)
        rules.append(rule)
    await db.flush()
    for r in rules:
        await db.refresh(r)
    return rules


async def check_health(api_base_url: str, timeout: int = 10) -> dict:
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            resp = await client.get(f"{api_base_url}/api/health")
            if resp.status_code == 200:
                return {"status": "ok", "data": resp.json()}
            return {"status": "error", "code": resp.status_code}
    except httpx.TimeoutException:
        return {"status": "timeout"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


async def search_artist_songs(
    api_base_url: str,
    artist_name: str,
    limit: int = 50,
    timeout: int = 10,
) -> list[dict]:
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            resp = await client.get(
                f"{api_base_url}/api/search",
                params={"keywords": artist_name, "limit": limit, "type": 1},
            )
            if resp.status_code != 200:
                return []
            data = resp.json()
            songs = data.get("result", {}).get("songs", [])
            return songs
    except Exception as e:
        logger.warning(f"Failed to search artist songs for {artist_name}: {e}")
        return []


async def get_song_detail(
    api_base_url: str,
    song_id: int,
    timeout: int = 10,
) -> dict | None:
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            resp = await client.get(f"{api_base_url}/api/song/detail", params={"ids": str(song_id)})
            if resp.status_code != 200:
                return None
            data = resp.json()
            songs = data.get("songs", [])
            return songs[0] if songs else None
    except Exception as e:
        logger.warning(f"Failed to get song detail for {song_id}: {e}")
        return None


async def get_song_url(
    api_base_url: str,
    song_id: int,
    timeout: int = 10,
) -> str | None:
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            resp = await client.get(f"{api_base_url}/api/song/url", params={"id": str(song_id)})
            if resp.status_code != 200:
                return None
            data = resp.json()
            urls = data.get("data", [])
            if urls and urls[0].get("url"):
                return urls[0]["url"]
            return None
    except Exception as e:
        logger.warning(f"Failed to get song URL for {song_id}: {e}")
        return None


async def sync_candidates_for_rule(
    db: AsyncSession,
    config: NetEaseApiConfig,
    rule: MusicSourceRule,
) -> int:
    log = MusicSyncLog(
        source_rule_id=rule.id,
        action="sync_candidates",
        status="running",
    )
    db.add(log)
    await db.flush()

    try:
        if rule.source_type == "artist":
            songs = await search_artist_songs(
                config.api_base_url, rule.source_value, timeout=config.timeout_seconds
            )
        elif rule.source_type == "search":
            songs = await search_artist_songs(
                config.api_base_url, rule.source_value, limit=30, timeout=config.timeout_seconds
            )
        else:
            songs = []

        count = 0
        for song in songs:
            song_id = song.get("id")
            if not song_id:
                continue

            existing = await db.execute(
                select(MusicCandidate).where(MusicCandidate.netease_id == song_id)
            )
            if existing.scalar_one_or_none():
                continue

            artists = song.get("artists", [])
            artist_name = "/".join(a.get("name", "") for a in artists) if artists else ""
            album = song.get("album", {})
            album_name = album.get("name", "")
            artwork = album.get("picUrl", "")

            preview_url = await get_song_url(
                config.api_base_url, song_id, timeout=config.timeout_seconds
            )

            candidate = MusicCandidate(
                source_rule_id=rule.id,
                netease_id=song_id,
                title=song.get("name", ""),
                artist=artist_name,
                album=album_name,
                artwork_url=artwork if artwork else None,
                preview_url=preview_url,
                netease_url=f"https://music.163.com/#/song?id={song_id}",
                duration_ms=song.get("duration"),
                synced_at=datetime.now(timezone.utc),
            )
            db.add(candidate)
            count += 1

        log.status = "success"
        log.candidates_found = count
        await db.flush()
        return count

    except Exception as e:
        log.status = "error"
        log.error_message = str(e)[:1000]
        await db.flush()
        logger.error(f"Sync failed for rule {rule.id}: {e}")
        return 0


async def sync_all_candidates(db: AsyncSession) -> dict:
    config = await get_netease_config(db)
    rules = await ensure_default_source_rules(db)

    total = 0
    results = []
    for rule in rules:
        if not rule.enabled:
            continue
        count = await sync_candidates_for_rule(db, config, rule)
        total += count
        results.append({"rule": rule.source_value, "synced": count})

    return {"total_synced": total, "rules": results}


from app.services.ai_prompt_registry import build_text_messages, render_user_content
from app.services.ai_task_types import AiTaskType


async def _generate_ai_reason(title: str, artist: str | None, album: str | None, source_value: str | None) -> str | None:
    try:
        from app.services.ai_gateway import call_text

        song_info = f"歌曲: {title}"
        if artist:
            song_info += f"\n歌手: {artist}"
        if album:
            song_info += f"\n专辑: {album}"
        if source_value:
            song_info += f"\n推荐来源: {source_value}"

        user_content = render_user_content(
            AiTaskType.NETEASE_REASON,
            {"song_info": song_info},
        )
        messages = build_text_messages(AiTaskType.NETEASE_REASON, user_content)

        gw = await call_text(AiTaskType.NETEASE_REASON, messages)
        if not gw.success:
            raise RuntimeError(gw.error or "AI call failed")
        result = gw.data
        reason = result.strip()
        if reason and len(reason) >= 10:
            return reason
        return None
    except Exception as e:
        logger.warning(f"AI recommendation reason generation failed: {e}")
        return None


async def generate_daily_song(db: AsyncSession, target_date: date | None = None) -> DailySong | None:
    if target_date is None:
        target_date = date.today()

    existing = await db.execute(select(DailySong).where(DailySong.date == target_date))
    if existing.scalar_one_or_none():
        return None

    result = await db.execute(
        select(MusicCandidate, MusicSourceRule)
        .outerjoin(MusicSourceRule, MusicCandidate.source_rule_id == MusicSourceRule.id)
        .where(MusicCandidate.netease_id.isnot(None))
    )
    rows = result.all()

    if not rows:
        result = await db.execute(
            select(DailySong).order_by(DailySong.date.desc()).limit(1)
        )
        prev = result.scalar_one_or_none()
        if prev:
            return prev
        return None

    weighted = []
    for candidate, rule in rows:
        artist = candidate.artist or ""
        weight = 1.0
        for artist_name, w in ARTIST_WEIGHTS.items():
            if artist_name in artist:
                weight = w
                break
        weighted.append((candidate, rule, weight))

    total_weight = sum(w for _, _, w in weighted)
    r = random.uniform(0, total_weight)
    cumulative = 0.0
    chosen = weighted[0]
    for candidate, rule, weight in weighted:
        cumulative += weight
        if r <= cumulative:
            chosen = (candidate, rule, weight)
            break

    candidate, rule, _ = chosen

    ai_reason = await _generate_ai_reason(
        title=candidate.title,
        artist=candidate.artist,
        album=candidate.album,
        source_value=rule.source_value if rule else None,
    )

    if ai_reason:
        reason = ai_reason
    else:
        reason = f"今日推荐来自{candidate.artist or '未知艺术家'}"
        if rule:
            reason += f"（来源: {rule.source_value}）"

    daily = DailySong(
        date=target_date,
        timezone="Asia/Shanghai",
        netease_id=candidate.netease_id,
        title=candidate.title,
        artist=candidate.artist,
        album=candidate.album,
        artwork_url=candidate.artwork_url,
        preview_url=candidate.preview_url,
        netease_url=candidate.netease_url,
        recommendation_reason=reason,
        source_rule_id=candidate.source_rule_id,
        candidate_id=candidate.id,
    )
    db.add(daily)
    await db.flush()
    await db.refresh(daily)
    return daily


async def get_or_create_today_song(db: AsyncSession) -> DailySong | None:
    from zoneinfo import ZoneInfo
    now_shanghai = datetime.now(ZoneInfo("Asia/Shanghai"))
    if now_shanghai.hour < 8:
        today = (now_shanghai - timedelta(days=1)).date()
    else:
        today = now_shanghai.date()
    result = await db.execute(select(DailySong).where(DailySong.date == today))
    existing = result.scalar_one_or_none()
    if existing:
        return existing
    return await generate_daily_song(db, today)


async def get_song_history(db: AsyncSession, limit: int = 30) -> list[DailySong]:
    result = await db.execute(
        select(DailySong).order_by(DailySong.date.desc()).limit(limit)
    )
    return list(result.scalars().all())
