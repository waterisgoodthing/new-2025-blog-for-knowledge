from typing import TypeVar

from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.note import Subject
from app.models.taxonomy import Chapter, KnowledgePoint, KnowledgePointLink
from app.schemas.taxonomy import (
    ChapterCreate,
    ChapterUpdate,
    KnowledgePointCreate,
    KnowledgePointUpdate,
    SubjectCreate,
    SubjectUpdate,
)


class TaxonomyError(Exception):
    pass


class TaxonomyNotFound(TaxonomyError):
    pass


class TaxonomyConflict(TaxonomyError):
    pass


class TaxonomyValidationError(TaxonomyError):
    pass


ModelT = TypeVar("ModelT", Subject, Chapter, KnowledgePoint)


async def _one_or_none(session: AsyncSession, statement: Select) -> object | None:
    result = await session.execute(statement)
    return result.scalar_one_or_none()


async def _get_or_raise(
    session: AsyncSession,
    model: type[ModelT],
    item_id: int,
    label: str,
) -> ModelT:
    item = await session.get(model, item_id)
    if item is None:
        raise TaxonomyNotFound(f"{label} not found")
    return item


async def list_subjects(
    session: AsyncSession,
    *,
    is_active: bool | None = None,
) -> list[Subject]:
    statement = select(Subject)
    if is_active is not None:
        statement = statement.where(Subject.is_active == is_active)
    result = await session.execute(statement.order_by(Subject.sort_order, Subject.id))
    return list(result.scalars().all())


async def get_subject(session: AsyncSession, subject_id: int) -> Subject:
    return await _get_or_raise(session, Subject, subject_id, "Subject")


async def create_subject(session: AsyncSession, payload: SubjectCreate) -> Subject:
    duplicate = await _one_or_none(
        session,
        select(Subject).where(Subject.name == payload.name),
    )
    if duplicate is not None:
        raise TaxonomyConflict("Subject already exists")

    subject = Subject(**payload.model_dump())
    session.add(subject)
    await session.flush()
    await session.refresh(subject)
    return subject


async def update_subject(
    session: AsyncSession,
    subject_id: int,
    payload: SubjectUpdate,
) -> Subject:
    subject = await get_subject(session, subject_id)
    changes = payload.model_dump(exclude_unset=True)
    if "name" in changes:
        duplicate = await _one_or_none(
            session,
            select(Subject).where(
                Subject.name == changes["name"],
                Subject.id != subject_id,
            ),
        )
        if duplicate is not None:
            raise TaxonomyConflict("Subject already exists")

    for field, value in changes.items():
        setattr(subject, field, value)
    await session.flush()
    await session.refresh(subject)
    return subject


async def delete_subject(session: AsyncSession, subject_id: int) -> None:
    subject = await get_subject(session, subject_id)
    chapter = await _one_or_none(
        session,
        select(Chapter.id).where(Chapter.subject_id == subject_id).limit(1),
    )
    knowledge_point = await _one_or_none(
        session,
        select(KnowledgePoint.id).where(KnowledgePoint.subject_id == subject_id).limit(1),
    )
    if chapter is not None or knowledge_point is not None:
        raise TaxonomyConflict("Subject still has chapters or knowledge points")
    await session.delete(subject)
    await session.flush()


async def list_chapters(
    session: AsyncSession,
    *,
    subject_id: int | None = None,
    is_active: bool | None = None,
) -> list[Chapter]:
    statement = select(Chapter)
    if subject_id is not None:
        statement = statement.where(Chapter.subject_id == subject_id)
    if is_active is not None:
        statement = statement.where(Chapter.is_active == is_active)
    result = await session.execute(statement.order_by(Chapter.sort_order, Chapter.id))
    return list(result.scalars().all())


async def get_chapter(session: AsyncSession, chapter_id: int) -> Chapter:
    return await _get_or_raise(session, Chapter, chapter_id, "Chapter")


async def create_chapter(session: AsyncSession, payload: ChapterCreate) -> Chapter:
    await get_subject(session, payload.subject_id)
    duplicate = await _one_or_none(
        session,
        select(Chapter).where(
            Chapter.subject_id == payload.subject_id,
            Chapter.name == payload.name,
        ),
    )
    if duplicate is not None:
        raise TaxonomyConflict("Chapter already exists in this subject")

    chapter = Chapter(**payload.model_dump())
    session.add(chapter)
    await session.flush()
    await session.refresh(chapter)
    return chapter


async def update_chapter(
    session: AsyncSession,
    chapter_id: int,
    payload: ChapterUpdate,
) -> Chapter:
    chapter = await get_chapter(session, chapter_id)
    changes = payload.model_dump(exclude_unset=True)
    if "name" in changes:
        duplicate = await _one_or_none(
            session,
            select(Chapter).where(
                Chapter.subject_id == chapter.subject_id,
                Chapter.name == changes["name"],
                Chapter.id != chapter_id,
            ),
        )
        if duplicate is not None:
            raise TaxonomyConflict("Chapter already exists in this subject")

    for field, value in changes.items():
        setattr(chapter, field, value)
    await session.flush()
    await session.refresh(chapter)
    return chapter


async def delete_chapter(session: AsyncSession, chapter_id: int) -> None:
    chapter = await get_chapter(session, chapter_id)
    knowledge_point = await _one_or_none(
        session,
        select(KnowledgePoint.id).where(KnowledgePoint.chapter_id == chapter_id).limit(1),
    )
    if knowledge_point is not None:
        raise TaxonomyConflict("Chapter still has knowledge points")
    await session.delete(chapter)
    await session.flush()


async def list_knowledge_points(
    session: AsyncSession,
    *,
    subject_id: int | None = None,
    chapter_id: int | None = None,
    is_active: bool | None = None,
) -> list[KnowledgePoint]:
    statement = select(KnowledgePoint)
    if subject_id is not None:
        statement = statement.where(KnowledgePoint.subject_id == subject_id)
    if chapter_id is not None:
        statement = statement.where(KnowledgePoint.chapter_id == chapter_id)
    if is_active is not None:
        statement = statement.where(KnowledgePoint.is_active == is_active)
    result = await session.execute(
        statement.order_by(KnowledgePoint.sort_order, KnowledgePoint.id)
    )
    return list(result.scalars().all())


async def get_knowledge_point(
    session: AsyncSession,
    knowledge_point_id: int,
) -> KnowledgePoint:
    return await _get_or_raise(
        session,
        KnowledgePoint,
        knowledge_point_id,
        "Knowledge point",
    )


async def _validate_chapter_subject(
    session: AsyncSession,
    subject_id: int,
    chapter_id: int | None,
) -> None:
    await get_subject(session, subject_id)
    if chapter_id is None:
        return
    chapter = await get_chapter(session, chapter_id)
    if chapter.subject_id != subject_id:
        raise TaxonomyValidationError("Chapter does not belong to the selected subject")


async def create_knowledge_point(
    session: AsyncSession,
    payload: KnowledgePointCreate,
) -> KnowledgePoint:
    await _validate_chapter_subject(session, payload.subject_id, payload.chapter_id)
    duplicate = await _one_or_none(
        session,
        select(KnowledgePoint).where(
            KnowledgePoint.subject_id == payload.subject_id,
            KnowledgePoint.name == payload.name,
        ),
    )
    if duplicate is not None:
        raise TaxonomyConflict("Knowledge point already exists in this subject")

    knowledge_point = KnowledgePoint(**payload.model_dump())
    session.add(knowledge_point)
    await session.flush()
    await session.refresh(knowledge_point)
    return knowledge_point


async def update_knowledge_point(
    session: AsyncSession,
    knowledge_point_id: int,
    payload: KnowledgePointUpdate,
) -> KnowledgePoint:
    knowledge_point = await get_knowledge_point(session, knowledge_point_id)
    changes = payload.model_dump(exclude_unset=True)
    subject_id = changes.get("subject_id", knowledge_point.subject_id)
    chapter_id = changes.get("chapter_id", knowledge_point.chapter_id)
    await _validate_chapter_subject(session, subject_id, chapter_id)

    if "name" in changes or "subject_id" in changes:
        name = changes.get("name", knowledge_point.name)
        duplicate = await _one_or_none(
            session,
            select(KnowledgePoint).where(
                KnowledgePoint.subject_id == subject_id,
                KnowledgePoint.name == name,
                KnowledgePoint.id != knowledge_point_id,
            ),
        )
        if duplicate is not None:
            raise TaxonomyConflict("Knowledge point already exists in this subject")

    for field, value in changes.items():
        setattr(knowledge_point, field, value)
    await session.flush()
    await session.refresh(knowledge_point)
    return knowledge_point


async def delete_knowledge_point(
    session: AsyncSession,
    knowledge_point_id: int,
) -> None:
    knowledge_point = await get_knowledge_point(session, knowledge_point_id)
    link = await _one_or_none(
        session,
        select(KnowledgePointLink.id)
        .where(KnowledgePointLink.knowledge_point_id == knowledge_point_id)
        .limit(1),
    )
    if link is not None:
        raise TaxonomyConflict("Knowledge point is still in use")
    await session.delete(knowledge_point)
    await session.flush()
