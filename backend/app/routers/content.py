import os
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.database import get_db
from app.models.note import User
from app.routers.auth import get_current_admin, get_passkey_admin
from app.schemas.content import (
    AboutContent,
    BloggerItem,
    DeleteManagedImageRequest,
    PictureItem,
    ProjectItem,
    ShareItem,
    SiteSettingsPayload,
)
from app.services.content_store import get_content, save_content

router = APIRouter(prefix="/api/content", tags=["content"])

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
PUBLIC_IMAGES_DIR = PROJECT_ROOT / "backend" / "public" / "images"
MAX_IMAGE_UPLOAD_BYTES = 10 * 1024 * 1024
UPLOAD_CHUNK_BYTES = 1024 * 1024
ALLOWED_UPLOAD_SCOPES = {"share", "project", "pictures", "blogger", "site"}


def _image_extension_from_header(header: bytes) -> str | None:
    if header.startswith(b"\x89PNG\r\n\x1a\n"):
        return ".png"
    if header.startswith(b"\xff\xd8\xff"):
        return ".jpg"
    if header.startswith((b"GIF87a", b"GIF89a")):
        return ".gif"
    if header.startswith(b"RIFF") and header[8:12] == b"WEBP":
        return ".webp"
    return None


def _normalize_group(group: str | None) -> str | None:
    if not group:
        return None
    return group.replace("/", "_").replace("..", "").strip()


def _relative_image_path(scope: str, filename: str, group: str | None = None) -> str:
    if group:
        return f"/images/{scope}/{group}/{filename}"
    return f"/images/{scope}/{filename}"


def _absolute_image_url(relative_path: str) -> str:
    return f"{get_settings().IMAGE_BASE_URL.rstrip('/')}{relative_path}"


def _resolve_managed_image_file(url: str) -> Path | None:
    relative = url
    image_base = get_settings().IMAGE_BASE_URL.rstrip("/")
    if relative.startswith(image_base):
        relative = relative[len(image_base):]
    if not relative.startswith("/images/"):
        return None
    relative = relative.removeprefix("/images/")
    parts = [part for part in relative.split("/") if part]
    if not parts or parts[0] not in ALLOWED_UPLOAD_SCOPES:
        return None
    return PUBLIC_IMAGES_DIR.joinpath(*parts)


@router.get("/about", response_model=AboutContent)
async def get_about_content(db: AsyncSession = Depends(get_db)):
    return await get_content(db, "about")


@router.put("/about", response_model=AboutContent)
async def update_about_content(
    payload: AboutContent,
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(get_current_admin),
):
    return await save_content(db, "about", payload.model_dump())


@router.get("/shares", response_model=list[ShareItem])
async def list_shares(db: AsyncSession = Depends(get_db)):
    return await get_content(db, "shares")


@router.put("/shares", response_model=list[ShareItem])
async def update_shares(
    payload: list[ShareItem],
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(get_current_admin),
):
    return await save_content(db, "shares", [item.model_dump() for item in payload])


@router.get("/projects", response_model=list[ProjectItem])
async def list_projects(db: AsyncSession = Depends(get_db)):
    return await get_content(db, "projects")


@router.put("/projects", response_model=list[ProjectItem])
async def update_projects(
    payload: list[ProjectItem],
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(get_current_admin),
):
    return await save_content(db, "projects", [item.model_dump() for item in payload])


@router.get("/pictures", response_model=list[PictureItem])
async def list_pictures(db: AsyncSession = Depends(get_db)):
    return await get_content(db, "pictures")


@router.put("/pictures", response_model=list[PictureItem])
async def update_pictures(
    payload: list[PictureItem],
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(get_current_admin),
):
    return await save_content(db, "pictures", [item.model_dump() for item in payload])


@router.get("/snippets", response_model=list[str])
async def list_snippets(db: AsyncSession = Depends(get_db)):
    return await get_content(db, "snippets")


@router.put("/snippets", response_model=list[str])
async def update_snippets(
    payload: list[str],
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(get_current_admin),
):
    return await save_content(db, "snippets", payload)


@router.get("/bloggers", response_model=list[BloggerItem])
async def list_bloggers(db: AsyncSession = Depends(get_db)):
    return await get_content(db, "bloggers")


@router.put("/bloggers", response_model=list[BloggerItem])
async def update_bloggers(
    payload: list[BloggerItem],
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(get_current_admin),
):
    return await save_content(db, "bloggers", [item.model_dump() for item in payload])


@router.get("/site-settings", response_model=SiteSettingsPayload)
async def get_site_settings(db: AsyncSession = Depends(get_db)):
    return await get_content(db, "site-settings")


@router.put("/site-settings", response_model=SiteSettingsPayload)
async def update_site_settings(
    payload: SiteSettingsPayload,
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(get_passkey_admin),
):
    return await save_content(db, "site-settings", payload.model_dump())


@router.post("/upload-image")
async def upload_managed_image(
    file: UploadFile = File(...),
    scope: str = Query(...),
    group: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(get_current_admin),
):
    if scope not in ALLOWED_UPLOAD_SCOPES:
        raise HTTPException(status_code=400, detail="Unsupported image scope")

    content_type = file.content_type
    if not (content_type and content_type.startswith("image/")):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File must be an image")

    header = await file.read(12)
    ext = _image_extension_from_header(header)
    if ext is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be a PNG, JPEG, GIF, or WebP image",
        )

    safe_group = _normalize_group(group)
    upload_dir = PUBLIC_IMAGES_DIR / scope
    if safe_group:
        upload_dir = upload_dir / safe_group
    os.makedirs(upload_dir, exist_ok=True)

    filename = f"{uuid.uuid4().hex[:12]}{ext}"
    file_path = upload_dir / filename
    total_bytes = len(header)

    try:
        with open(file_path, "wb") as f:
            f.write(header)
            while True:
                chunk = await file.read(UPLOAD_CHUNK_BYTES)
                if not chunk:
                    break
                total_bytes += len(chunk)
                if total_bytes > MAX_IMAGE_UPLOAD_BYTES:
                    raise HTTPException(
                        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                        detail="File too large (max 10MB)",
                    )
                f.write(chunk)
    except HTTPException:
        file_path.unlink(missing_ok=True)
        raise

    relative_path = _relative_image_path(scope, filename, safe_group)
    return {"url": _absolute_image_url(relative_path), "path": relative_path}


@router.delete("/delete-image")
async def delete_managed_image(
    payload: DeleteManagedImageRequest,
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(get_current_admin),
):
    target = _resolve_managed_image_file(payload.url)
    if target is None:
        raise HTTPException(status_code=400, detail="Unsupported image url")
    target.unlink(missing_ok=True)
    return {"message": "Image deleted"}
