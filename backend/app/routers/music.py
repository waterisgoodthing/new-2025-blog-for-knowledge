import httpx
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.music import MusicItem
from app.routers.auth import get_current_admin
from app.schemas.music import MusicItemCreate, MusicItemOut, MusicItemUpdate

router = APIRouter(prefix="/api/music", tags=["music"])

ITUNES_LOOKUP_URL = "https://itunes.apple.com/lookup"


def _extract_track_id(url: str) -> int | None:
    import re

    match = re.search(r"[?&]i=(\d+)", url)
    if match:
        return int(match.group(1))
    match = re.search(r"/id(\d+)", url)
    if match:
        return int(match.group(1))
    return None


async def _fetch_itunes_metadata(track_id: int, country: str = "cn") -> dict | None:
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(
                ITUNES_LOOKUP_URL,
                params={"id": track_id, "country": country},
            )
            if resp.status_code == 200:
                data = resp.json()
                if data.get("resultCount", 0) > 0:
                    return data["results"][0]
    except Exception:
        pass
    return None


@router.get("/playlist", response_model=list[MusicItemOut])
async def get_playlist(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(MusicItem).where(MusicItem.is_active == True).order_by(MusicItem.sort_order)
    )
    return result.scalars().all()


@router.post("/items", response_model=MusicItemOut)
async def create_music_item(
    req: MusicItemCreate, db: AsyncSession = Depends(get_db), _admin=Depends(get_current_admin)
):
    track_id = req.track_id or _extract_track_id(req.apple_music_url)

    item = MusicItem(
        title=req.title,
        artist=req.artist,
        artwork=req.artwork,
        apple_music_url=req.apple_music_url,
        preview_url=req.preview_url,
        track_id=track_id,
        sort_order=req.sort_order,
        is_active=req.is_active,
    )

    if track_id and not req.artist:
        meta = await _fetch_itunes_metadata(track_id)
        if meta:
            item.artist = meta.get("artistName", item.artist)
            item.artwork = meta.get("artworkUrl100", item.artwork)
            item.preview_url = meta.get("previewUrl", item.preview_url)

    db.add(item)
    await db.flush()
    await db.refresh(item)
    return item


@router.put("/items/{item_id}", response_model=MusicItemOut)
async def update_music_item(
    item_id: int,
    req: MusicItemUpdate,
    db: AsyncSession = Depends(get_db),
    _admin=Depends(get_current_admin),
):
    result = await db.execute(select(MusicItem).where(MusicItem.id == item_id))
    item = result.scalar_one_or_none()
    if item is None:
        raise HTTPException(status_code=404, detail="Music item not found")

    update_data = req.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(item, key, value)

    if req.apple_music_url and not req.track_id:
        track_id = _extract_track_id(req.apple_music_url)
        if track_id:
            item.track_id = track_id

    await db.flush()
    await db.refresh(item)
    return item


@router.delete("/items/{item_id}")
async def delete_music_item(item_id: int, db: AsyncSession = Depends(get_db), _admin=Depends(get_current_admin)):
    result = await db.execute(select(MusicItem).where(MusicItem.id == item_id))
    item = result.scalar_one_or_none()
    if item is None:
        raise HTTPException(status_code=404, detail="Music item not found")
    await db.delete(item)
    return {"ok": True}
