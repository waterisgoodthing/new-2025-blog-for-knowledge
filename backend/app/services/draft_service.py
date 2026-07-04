import uuid
from dataclasses import dataclass

from pydantic import ValidationError
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.note import Subject
from app.models.question import DraftItem, Question, QuestionDraft, QuestionSource
from app.models.taxonomy import KnowledgePoint, KnowledgePointLink
from app.schemas.question import QuestionDraftCreate, QuestionDraftUpdate
from app.services.question_service import QuestionRecord, get_question


class DraftError(Exception):
    pass


class DraftNotFound(DraftError):
    pass


class DraftConflict(DraftError):
    pass


class DraftValidationError(DraftError):
    pass


@dataclass
class QuestionDraftRecord:
    item: DraftItem
    draft: QuestionDraft
    knowledge_point_ids: list[int]

    def __getattr__(self, name: str):
        return getattr(self.draft, name)


async def list_question_drafts(
    session: AsyncSession,
    *,
    status: str | None = None,
) -> list[QuestionDraftRecord]:
    statement = (
        select(DraftItem, QuestionDraft)
        .join(QuestionDraft, QuestionDraft.draft_item_id == DraftItem.id)
        .where(DraftItem.draft_type == "question")
    )
    if status is not None:
        statement = statement.where(DraftItem.status == status)
    rows = (
        await session.execute(
            statement.order_by(DraftItem.updated_at.desc(), DraftItem.id)
        )
    ).all()
    records = []
    for item, draft in rows:
        records.append(
            QuestionDraftRecord(
                item=item,
                draft=draft,
                knowledge_point_ids=await _knowledge_point_ids(
                    session,
                    "question_draft",
                    draft.id,
                ),
            )
        )
    return records


async def _validate_taxonomy(
    session: AsyncSession,
    subject_id: int,
    knowledge_point_ids: list[int],
) -> None:
    if await session.get(Subject, subject_id) is None:
        raise DraftNotFound("Subject not found")
    if not knowledge_point_ids:
        return
    result = await session.execute(
        select(KnowledgePoint).where(KnowledgePoint.id.in_(knowledge_point_ids))
    )
    points = list(result.scalars().all())
    if len(points) != len(knowledge_point_ids):
        raise DraftNotFound("Knowledge point not found")
    if any(point.subject_id != subject_id for point in points):
        raise DraftValidationError("Knowledge points must belong to the selected subject")


async def _knowledge_point_ids(
    session: AsyncSession,
    target_type: str,
    target_id: uuid.UUID,
) -> list[int]:
    result = await session.execute(
        select(KnowledgePointLink.knowledge_point_id)
        .where(
            KnowledgePointLink.target_type == target_type,
            KnowledgePointLink.target_id == str(target_id),
        )
        .order_by(KnowledgePointLink.knowledge_point_id)
    )
    return list(result.scalars().all())


async def create_question_draft(
    session: AsyncSession,
    payload: QuestionDraftCreate,
    *,
    created_by: uuid.UUID | None = None,
) -> QuestionDraftRecord:
    await _validate_taxonomy(
        session,
        payload.subject_id,
        payload.knowledge_point_ids,
    )
    item = DraftItem(
        draft_type="question",
        source_type="manual",
        status="pending",
        created_by=created_by,
    )
    session.add(item)
    await session.flush()

    values = payload.model_dump(exclude={"knowledge_point_ids"})
    draft = QuestionDraft(draft_item_id=item.id, **values)
    session.add(draft)
    await session.flush()

    for knowledge_point_id in payload.knowledge_point_ids:
        session.add(
            KnowledgePointLink(
                knowledge_point_id=knowledge_point_id,
                target_type="question_draft",
                target_id=str(draft.id),
            )
        )
    await session.flush()
    await session.refresh(item)
    await session.refresh(draft)
    return QuestionDraftRecord(
        item=item,
        draft=draft,
        knowledge_point_ids=sorted(payload.knowledge_point_ids),
    )


async def get_question_draft(
    session: AsyncSession,
    draft_item_id: uuid.UUID,
    *,
    for_update: bool = False,
) -> QuestionDraftRecord:
    statement = select(DraftItem).where(DraftItem.id == draft_item_id)
    if for_update:
        statement = statement.with_for_update()
    item = (await session.execute(statement)).scalar_one_or_none()
    if item is None or item.draft_type != "question":
        raise DraftNotFound("Question draft not found")
    draft = (
        await session.execute(
            select(QuestionDraft).where(QuestionDraft.draft_item_id == item.id)
        )
    ).scalar_one_or_none()
    if draft is None:
        raise DraftNotFound("Question draft details not found")
    return QuestionDraftRecord(
        item=item,
        draft=draft,
        knowledge_point_ids=await _knowledge_point_ids(
            session,
            "question_draft",
            draft.id,
        ),
    )


async def update_question_draft(
    session: AsyncSession,
    draft_item_id: uuid.UUID,
    payload: QuestionDraftUpdate,
) -> QuestionDraftRecord:
    record = await get_question_draft(session, draft_item_id, for_update=True)
    if record.item.status in {"converted", "rejected"}:
        raise DraftConflict(f"Cannot edit a {record.item.status} draft")
    if payload.version != record.item.version:
        raise DraftConflict("Draft version conflict")

    changes = payload.model_dump(exclude={"version"}, exclude_unset=True)
    current = {
        "subject_id": record.subject_id,
        "title": record.title,
        "question_text": record.question_text,
        "question_type": record.question_type,
        "options": record.options,
        "correct_answer": record.correct_answer,
        "explanation": record.explanation,
        "difficulty": record.difficulty,
        "knowledge_point_ids": record.knowledge_point_ids,
    }
    try:
        validated = QuestionDraftCreate.model_validate({**current, **changes})
    except ValidationError as error:
        raise DraftValidationError(str(error)) from error
    await _validate_taxonomy(
        session,
        validated.subject_id,
        validated.knowledge_point_ids,
    )

    values = validated.model_dump(exclude={"knowledge_point_ids"})
    for field, value in values.items():
        setattr(record.draft, field, value)

    if "knowledge_point_ids" in changes:
        await session.execute(
            delete(KnowledgePointLink).where(
                KnowledgePointLink.target_type == "question_draft",
                KnowledgePointLink.target_id == str(record.draft.id),
            )
        )
        for knowledge_point_id in validated.knowledge_point_ids:
            session.add(
                KnowledgePointLink(
                    knowledge_point_id=knowledge_point_id,
                    target_type="question_draft",
                    target_id=str(record.draft.id),
                )
            )

    record.item.version += 1
    record.item.validation_errors = []
    record.item.status = "pending"
    await session.flush()
    await session.refresh(record.item)
    await session.refresh(record.draft)
    return QuestionDraftRecord(
        item=record.item,
        draft=record.draft,
        knowledge_point_ids=sorted(validated.knowledge_point_ids),
    )


async def convert_question_draft(
    session: AsyncSession,
    draft_item_id: uuid.UUID,
    *,
    version: int,
) -> QuestionRecord:
    record = await get_question_draft(session, draft_item_id, for_update=True)
    if record.item.status == "converted":
        if record.item.target_id is None:
            raise DraftConflict("Converted draft has no target")
        return await get_question(session, uuid.UUID(record.item.target_id))
    if record.item.status == "rejected":
        raise DraftConflict("Rejected drafts cannot be converted")
    if version != record.item.version:
        raise DraftConflict("Draft version conflict")

    validated = QuestionDraftCreate(
        subject_id=record.subject_id,
        title=record.title,
        question_text=record.question_text,
        question_type=record.question_type,
        options=record.options,
        correct_answer=record.correct_answer,
        explanation=record.explanation,
        difficulty=record.difficulty,
        knowledge_point_ids=record.knowledge_point_ids,
    )
    await _validate_taxonomy(
        session,
        validated.subject_id,
        validated.knowledge_point_ids,
    )

    question = Question(
        **validated.model_dump(exclude={"knowledge_point_ids"}),
        status="active",
        visibility="private",
        version=1,
    )
    session.add(question)
    await session.flush()
    source = QuestionSource(
        question_id=question.id,
        source_type="manual",
        source_name="手工录入",
        source_ref=str(record.item.id),
    )
    session.add(source)
    for knowledge_point_id in validated.knowledge_point_ids:
        session.add(
            KnowledgePointLink(
                knowledge_point_id=knowledge_point_id,
                target_type="question",
                target_id=str(question.id),
            )
        )

    record.item.status = "converted"
    record.item.target_type = "question"
    record.item.target_id = str(question.id)
    record.item.version += 1
    await session.flush()
    await session.refresh(record.item)
    await session.refresh(question)
    await session.refresh(source)
    return QuestionRecord(
        question=question,
        sources=[source],
        knowledge_point_ids=sorted(validated.knowledge_point_ids),
    )


async def reject_question_draft(
    session: AsyncSession,
    draft_item_id: uuid.UUID,
    *,
    version: int,
) -> QuestionDraftRecord:
    record = await get_question_draft(session, draft_item_id, for_update=True)
    if record.item.status == "converted":
        raise DraftConflict("Converted drafts cannot be rejected")
    if record.item.status == "rejected":
        return record
    if version != record.item.version:
        raise DraftConflict("Draft version conflict")
    record.item.status = "rejected"
    record.item.version += 1
    await session.flush()
    await session.refresh(record.item)
    return record
