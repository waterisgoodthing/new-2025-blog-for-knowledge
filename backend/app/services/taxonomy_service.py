from typing import TypeVar

from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.note import Subject
from app.models.taxonomy import KnowledgePoint, KnowledgePointLink
from app.schemas.taxonomy import (
    KnowledgePointCreate,
    KnowledgePointTreeNode,
    KnowledgePointUpdate,
    KnowledgeTreeOut,
    SubjectCreate,
    SubjectSummary,
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


ModelT = TypeVar("ModelT", Subject, KnowledgePoint)


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
    status: str | None = None,
) -> list[Subject]:
    statement = select(Subject)
    if status is not None:
        statement = statement.where(Subject.status == status)
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
    knowledge_point = await _one_or_none(
        session,
        select(KnowledgePoint.id).where(KnowledgePoint.subject_id == subject_id).limit(1),
    )
    if knowledge_point is not None:
        raise TaxonomyConflict("Subject still has knowledge points")
    await session.delete(subject)
    await session.flush()


async def list_knowledge_points(
    session: AsyncSession,
    *,
    subject_id: int | None = None,
    parent_id: int | None = None,
    status: str | None = None,
) -> list[KnowledgePoint]:
    statement = select(KnowledgePoint)
    if subject_id is not None:
        statement = statement.where(KnowledgePoint.subject_id == subject_id)
    if parent_id is not None:
        statement = statement.where(KnowledgePoint.parent_id == parent_id)
    if status is not None:
        statement = statement.where(KnowledgePoint.status == status)
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


async def _validate_parent(
    session: AsyncSession,
    *,
    subject_id: int,
    parent_id: int | None,
    moving_id: int | None = None,
) -> None:
    await get_subject(session, subject_id)
    if parent_id is None:
        return
    if moving_id is not None and parent_id == moving_id:
        raise TaxonomyValidationError("Knowledge point cannot be its own parent")

    parent = await get_knowledge_point(session, parent_id)
    if parent.subject_id != subject_id:
        raise TaxonomyValidationError("Parent does not belong to the selected subject")

    if moving_id is None:
        return

    current_parent_id = parent.parent_id
    while current_parent_id is not None:
        if current_parent_id == moving_id:
            raise TaxonomyValidationError("Knowledge point cannot move under its descendant")
        ancestor = await get_knowledge_point(session, current_parent_id)
        current_parent_id = ancestor.parent_id


async def create_knowledge_point(
    session: AsyncSession,
    payload: KnowledgePointCreate,
) -> KnowledgePoint:
    await _validate_parent(
        session,
        subject_id=payload.subject_id,
        parent_id=payload.parent_id,
    )
    duplicate = await _one_or_none(
        session,
        select(KnowledgePoint).where(
            KnowledgePoint.subject_id == payload.subject_id,
            KnowledgePoint.parent_id == payload.parent_id,
            func.lower(KnowledgePoint.name) == func.lower(payload.name),
        ),
    )
    if duplicate is not None:
        raise TaxonomyConflict("Knowledge point already exists under this parent")

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
    parent_id = changes.get("parent_id", knowledge_point.parent_id)
    await _validate_parent(
        session,
        subject_id=subject_id,
        parent_id=parent_id,
        moving_id=knowledge_point_id,
    )

    if {"name", "subject_id", "parent_id"}.intersection(changes):
        name = changes.get("name", knowledge_point.name)
        duplicate = await _one_or_none(
            session,
            select(KnowledgePoint).where(
                KnowledgePoint.subject_id == subject_id,
                KnowledgePoint.parent_id == parent_id,
                func.lower(KnowledgePoint.name) == func.lower(name),
                KnowledgePoint.id != knowledge_point_id,
            ),
        )
        if duplicate is not None:
            raise TaxonomyConflict("Knowledge point already exists under this parent")

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
    child = await _one_or_none(
        session,
        select(KnowledgePoint.id).where(KnowledgePoint.parent_id == knowledge_point_id).limit(1),
    )
    if child is not None:
        raise TaxonomyConflict("Knowledge point still has children")
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


async def archive_knowledge_point(
    session: AsyncSession,
    knowledge_point_id: int,
) -> KnowledgePoint:
    root = await get_knowledge_point(session, knowledge_point_id)
    descendants = await _collect_descendants(session, knowledge_point_id)
    for item in [root, *descendants]:
        item.status = "archived"
    await session.flush()
    await session.refresh(root)
    return root


async def _collect_descendants(
    session: AsyncSession,
    knowledge_point_id: int,
) -> list[KnowledgePoint]:
    result = await session.execute(
        select(KnowledgePoint)
        .where(KnowledgePoint.parent_id == knowledge_point_id)
        .order_by(KnowledgePoint.sort_order, KnowledgePoint.id)
    )
    children = list(result.scalars().all())
    descendants: list[KnowledgePoint] = []
    for child in children:
        descendants.append(child)
        descendants.extend(await _collect_descendants(session, child.id))
    return descendants


async def get_subject_knowledge_tree(
    session: AsyncSession,
    subject_id: int,
    *,
    status: str | None = None,
) -> KnowledgeTreeOut:
    subject = await get_subject(session, subject_id)
    points = await list_knowledge_points(session, subject_id=subject_id, status=status)
    by_parent: dict[int | None, list[KnowledgePoint]] = {}
    for point in points:
        by_parent.setdefault(point.parent_id, []).append(point)

    def build(point: KnowledgePoint) -> KnowledgePointTreeNode:
        return KnowledgePointTreeNode(
            id=point.id,
            subject_id=point.subject_id,
            parent_id=point.parent_id,
            name=point.name,
            description=point.description,
            status=point.status,
            sort_order=point.sort_order,
            created_at=point.created_at,
            updated_at=point.updated_at,
            children=[build(child) for child in by_parent.get(point.id, [])],
        )

    roots = [build(point) for point in by_parent.get(None, [])]
    return KnowledgeTreeOut(
        subject=SubjectSummary.model_validate(subject),
        nodes=roots,
    )
