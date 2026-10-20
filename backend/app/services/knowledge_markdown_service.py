import re
from dataclasses import dataclass
from typing import Sequence

from sqlalchemy import Text, and_, cast, desc, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.knowledge_markdown import NoteLink, NoteVersion
from app.models.note import Note

WIKILINK_PATTERN = re.compile(r"\[\[([^\]|#]+)(?:#[^\]|]+)?(?:\|[^\]]+)?\]\]")


@dataclass(frozen=True)
class SearchQuery:
    query: str
    limit: int = 50


def extract_wikilinks(content: str) -> list[str]:
    return list(dict.fromkeys(match.strip() for match in WIKILINK_PATTERN.findall(content or "") if match.strip()))


async def create_initial_version(session: AsyncSession, note: Note, *, created_by=None) -> NoteVersion:
    version = NoteVersion(note_id=note.id, version=note.revision, title=note.title, content=note.content, created_by=created_by)
    session.add(version)
    await session.flush()
    return version


async def create_next_version(session: AsyncSession, note: Note, *, created_by=None) -> NoteVersion:
    note.revision += 1
    version = NoteVersion(note_id=note.id, version=note.revision, title=note.title, content=note.content, created_by=created_by)
    session.add(version)
    await session.flush()
    return version


async def list_note_versions(session: AsyncSession, note_id) -> list[NoteVersion]:
    return list((await session.scalars(select(NoteVersion).where(NoteVersion.note_id == note_id).order_by(desc(NoteVersion.version)))).all())


async def sync_wikilinks(session: AsyncSession, source: Note) -> list[NoteLink]:
    old = list((await session.scalars(select(NoteLink).where(NoteLink.source_note_id == source.id))).all())
    for link in old:
        await session.delete(link)
    await session.flush()
    slugs = extract_wikilinks(source.content)
    if not slugs:
        return []
    targets = {
        note.slug: note
        for note in (await session.scalars(select(Note).where(Note.slug.in_(slugs)))).all()
    }
    links = [
        NoteLink(source_note_id=source.id, target_note_id=targets.get(slug).id if slug in targets else None, target_slug=slug, raw_link=slug)
        for slug in slugs
    ]
    session.add_all(links)
    await session.flush()
    return links


async def list_backlinks(session: AsyncSession, target_note_id) -> list[NoteLink]:
    return list((await session.scalars(select(NoteLink).where(NoteLink.target_note_id == target_note_id).order_by(NoteLink.created_at))).all())


async def search_notes(session: AsyncSession, request: SearchQuery) -> list[Note]:
    query = request.query.strip()
    if not query:
        return []
    haystack = func.concat(Note.title, " ", Note.content, " ", func.coalesce(Note.summary, ""), " ", func.coalesce(Note.category, ""))
    vector_match = func.to_tsvector("simple", haystack).op("@@")(func.plainto_tsquery("simple", query))
    score = func.greatest(func.similarity(Note.title, query), func.similarity(cast(haystack, Text), query))
    statement = (
        select(Note)
        .where(Note.hidden.is_(False), Note.status == "published")
        .where(or_(vector_match, score >= 0.12))
        .order_by(desc(score), desc(Note.updated_at))
        .limit(request.limit)
    )
    return list((await session.scalars(statement)).all())
