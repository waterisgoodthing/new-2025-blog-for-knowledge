import re
import unicodedata

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.note import Note


def generate_slug(text: str) -> str:
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode("ascii")
    text = re.sub(r"[^\w\s-]", "", text).strip().lower()
    return re.sub(r"[-\s]+", "-", text)


async def ensure_unique_slug(db: AsyncSession, base_slug: str) -> str:
    candidate = base_slug
    suffix = 2
    while True:
        existing = await db.execute(select(Note.id).where(Note.slug == candidate).limit(1))
        if existing.scalar_one_or_none() is None:
            return candidate
        candidate = f"{base_slug}-{suffix}"
        suffix += 1
