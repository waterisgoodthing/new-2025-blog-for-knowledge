import json
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.content import ManagedContentEntry

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent

CONTENT_DEFAULTS: dict[str, object] = {
    "about": PROJECT_ROOT / "src" / "app" / "about" / "list.json",
    "shares": PROJECT_ROOT / "src" / "app" / "share" / "list.json",
    "projects": PROJECT_ROOT / "src" / "app" / "projects" / "list.json",
    "pictures": PROJECT_ROOT / "src" / "app" / "pictures" / "list.json",
    "snippets": PROJECT_ROOT / "src" / "app" / "snippets" / "list.json",
    "bloggers": PROJECT_ROOT / "src" / "app" / "bloggers" / "list.json",
}

SITE_CONTENT_PATH = PROJECT_ROOT / "src" / "config" / "site-content.json"
CARD_STYLES_PATH = PROJECT_ROOT / "src" / "config" / "card-styles.json"


def _read_json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def _site_settings_default() -> dict:
    site_content = _read_json(SITE_CONTENT_PATH)
    if isinstance(site_content, dict):
        site_content.setdefault("faviconUrl", "/favicon.png")
        site_content.setdefault("avatarUrl", "/images/avatar.png")
    return {
        "siteContent": site_content,
        "cardStyles": _read_json(CARD_STYLES_PATH),
    }


def get_default_content(key: str) -> object:
    if key == "site-settings":
        return _site_settings_default()

    source = CONTENT_DEFAULTS[key]
    if isinstance(source, Path):
        return _read_json(source)
    return source


async def get_or_create_content_entry(db: AsyncSession, key: str) -> ManagedContentEntry:
    result = await db.execute(select(ManagedContentEntry).where(ManagedContentEntry.key == key))
    entry = result.scalar_one_or_none()
    if entry is not None:
        return entry

    entry = ManagedContentEntry(key=key, data=get_default_content(key))
    db.add(entry)
    await db.flush()
    return entry


async def get_content(db: AsyncSession, key: str):
    entry = await get_or_create_content_entry(db, key)
    return entry.data


async def save_content(db: AsyncSession, key: str, data: object):
    entry = await get_or_create_content_entry(db, key)
    entry.data = data
    db.add(entry)
    await db.flush()
    return entry.data
