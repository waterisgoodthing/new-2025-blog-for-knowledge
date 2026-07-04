import uuid
from dataclasses import dataclass

from pydantic import ValidationError
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.note import Subject
from app.models.question import Question, QuestionSource
from app.models.taxonomy import KnowledgePoint, KnowledgePointLink
from app.schemas.question import QuestionDraftCreate, QuestionUpdate


class QuestionError(Exception):
    pass


class QuestionNotFound(QuestionError):
    pass


class QuestionConflict(QuestionError):
    pass


class QuestionValidationError(QuestionError):
    pass


@dataclass
class QuestionRecord:
    question: Question
    sources: list[QuestionSource]
    knowledge_point_ids: list[int]

    def __getattr__(self, name: str):
        return getattr(self.question, name)


async def list_questions(
    session: AsyncSession,
    *,
    subject_id: int | None = None,
    status: str | None = None,
) -> list[QuestionRecord]:
    statement = select(Question)
    if subject_id is not None:
        statement = statement.where(Question.subject_id == subject_id)
    if status is not None:
        statement = statement.where(Question.status == status)
    questions = list(
        (
            await session.execute(
                statement.order_by(Question.updated_at.desc(), Question.id)
            )
        )
        .scalars()
        .all()
    )
    return [await get_question(session, question.id) for question in questions]


async def get_question(
    session: AsyncSession,
    question_id: uuid.UUID,
) -> QuestionRecord:
    question = await session.get(Question, question_id)
    if question is None:
        raise QuestionNotFound("Question not found")
    sources = list(
        (
            await session.execute(
                select(QuestionSource)
                .where(QuestionSource.question_id == question_id)
                .order_by(QuestionSource.created_at, QuestionSource.id)
            )
        )
        .scalars()
        .all()
    )
    knowledge_point_ids = list(
        (
            await session.execute(
                select(KnowledgePointLink.knowledge_point_id)
                .where(
                    KnowledgePointLink.target_type == "question",
                    KnowledgePointLink.target_id == str(question_id),
                )
                .order_by(KnowledgePointLink.knowledge_point_id)
            )
        )
        .scalars()
        .all()
    )
    return QuestionRecord(
        question=question,
        sources=sources,
        knowledge_point_ids=knowledge_point_ids,
    )


async def _validate_taxonomy(
    session: AsyncSession,
    subject_id: int,
    knowledge_point_ids: list[int],
) -> None:
    if await session.get(Subject, subject_id) is None:
        raise QuestionNotFound("Subject not found")
    if not knowledge_point_ids:
        return
    points = list(
        (
            await session.execute(
                select(KnowledgePoint).where(
                    KnowledgePoint.id.in_(knowledge_point_ids)
                )
            )
        )
        .scalars()
        .all()
    )
    if len(points) != len(knowledge_point_ids):
        raise QuestionNotFound("Knowledge point not found")
    if any(point.subject_id != subject_id for point in points):
        raise QuestionValidationError(
            "Knowledge points must belong to the selected subject"
        )


async def update_question(
    session: AsyncSession,
    question_id: uuid.UUID,
    payload: QuestionUpdate,
) -> QuestionRecord:
    question = (
        await session.execute(
            select(Question)
            .where(Question.id == question_id)
            .with_for_update()
        )
    ).scalar_one_or_none()
    if question is None:
        raise QuestionNotFound("Question not found")
    if payload.version != question.version:
        raise QuestionConflict("Question version conflict")

    current = await get_question(session, question_id)
    changes = payload.model_dump(exclude={"version"}, exclude_unset=True)
    try:
        validated = QuestionDraftCreate.model_validate(
            {
                "subject_id": question.subject_id,
                "title": question.title,
                "question_text": question.question_text,
                "question_type": question.question_type,
                "options": question.options,
                "correct_answer": question.correct_answer,
                "explanation": question.explanation,
                "difficulty": question.difficulty,
                "knowledge_point_ids": current.knowledge_point_ids,
                **changes,
            }
        )
    except ValidationError as error:
        raise QuestionValidationError(str(error)) from error
    await _validate_taxonomy(
        session,
        validated.subject_id,
        validated.knowledge_point_ids,
    )
    for field, value in validated.model_dump(
        exclude={"knowledge_point_ids"}
    ).items():
        setattr(question, field, value)

    if "knowledge_point_ids" in changes:
        await session.execute(
            delete(KnowledgePointLink).where(
                KnowledgePointLink.target_type == "question",
                KnowledgePointLink.target_id == str(question_id),
            )
        )
        for knowledge_point_id in validated.knowledge_point_ids:
            session.add(
                KnowledgePointLink(
                    knowledge_point_id=knowledge_point_id,
                    target_type="question",
                    target_id=str(question_id),
                )
            )
    question.version += 1
    await session.flush()
    await session.refresh(question)
    return await get_question(session, question_id)


async def archive_question(
    session: AsyncSession,
    question_id: uuid.UUID,
    *,
    version: int,
) -> QuestionRecord:
    question = (
        await session.execute(
            select(Question)
            .where(Question.id == question_id)
            .with_for_update()
        )
    ).scalar_one_or_none()
    if question is None:
        raise QuestionNotFound("Question not found")
    if question.status == "archived":
        return await get_question(session, question_id)
    if version != question.version:
        raise QuestionConflict("Question version conflict")
    question.status = "archived"
    question.version += 1
    await session.flush()
    await session.refresh(question)
    return await get_question(session, question_id)
