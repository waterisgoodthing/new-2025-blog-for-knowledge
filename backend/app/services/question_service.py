import uuid
from dataclasses import dataclass

from pydantic import ValidationError
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.note import Subject
from app.models.question import Question, QuestionKnowledgePoint, QuestionSource
from app.models.taxonomy import KnowledgePoint, KnowledgePointLink
from app.schemas.question import (
    QuestionCreate,
    QuestionDraftCreate,
    QuestionPatch,
    QuestionSourceCreate,
    QuestionUpdate,
)


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

    @property
    def stem_md(self) -> str:
        return self.question.stem_md or self.question.question_text

    @property
    def analysis_md(self) -> str | None:
        return self.question.analysis_md if self.question.analysis_md is not None else self.question.explanation

    @property
    def difficulty(self) -> str:
        return self.question.difficulty or "unspecified"

    @property
    def options(self) -> list[dict]:
        values = self.question.options or []
        if all(isinstance(item, dict) for item in values):
            return values
        return [{"key": chr(65 + index), "text": str(item)} for index, item in enumerate(values)]

    @property
    def answer_data(self) -> dict:
        if self.question.answer_data:
            return self.question.answer_data
        value = self.question.correct_answer
        if self.question.question_type in {"single_choice", "multiple_choice"}:
            answer = [item.strip() for item in (value or "").split(",") if item.strip()]
        elif self.question.question_type == "true_false":
            answer = value == "true"
        else:
            answer = value or ""
        return {"kind": self.question.question_type, "value": answer}


async def create_question(
    session: AsyncSession,
    payload: QuestionCreate,
) -> QuestionRecord:
    knowledge_point_ids = [link.knowledge_point_id for link in payload.knowledge_point_links]
    await _validate_taxonomy(session, payload.subject_id, knowledge_point_ids)
    answer_value = payload.answer_data.get("value")
    if isinstance(answer_value, list):
        legacy_answer = ",".join(str(item) for item in answer_value)
    else:
        legacy_answer = str(answer_value) if answer_value is not None else None
    analysis = payload.analysis_md
    question = Question(
        subject_id=payload.subject_id,
        title=payload.title,
        stem_md=payload.stem_md,
        question_text=payload.stem_md,
        question_type=payload.question_type,
        options=[option.model_dump() for option in payload.options],
        answer_data=payload.answer_data,
        correct_answer=legacy_answer,
        analysis_md=analysis,
        explanation=analysis,
        difficulty=payload.difficulty,
    )
    session.add(question)
    await session.flush()
    for link in payload.knowledge_point_links:
        session.add(
            QuestionKnowledgePoint(
                question_id=question.id,
                knowledge_point_id=link.knowledge_point_id,
                role=link.role,
                sort_order=link.sort_order,
            )
        )
        session.add(
            KnowledgePointLink(
                knowledge_point_id=link.knowledge_point_id,
                target_type="question",
                target_id=str(question.id),
            )
        )
    sources = payload.sources or [QuestionSourceCreate(source_type="manual", source_title="手工录入")]
    for source in sources:
        session.add(
            QuestionSource(
                question_id=question.id,
                source_type=source.source_type,
                source_name=source.source_title,
                source_title=source.source_title,
                source_ref=source.source_ref,
                source_url=source.source_url,
                source_note=source.source_note,
            )
        )
    await session.flush()
    await session.refresh(question)
    return await get_question(session, question.id)


async def list_questions(
    session: AsyncSession,
    *,
    subject_id: int | None = None,
    status: str | None = None,
    knowledge_point_id: int | None = None,
    question_type: str | None = None,
    difficulty: str | None = None,
) -> list[QuestionRecord]:
    statement = select(Question)
    if subject_id is not None:
        statement = statement.where(Question.subject_id == subject_id)
    if status is not None:
        statement = statement.where(Question.status == status)
    if question_type is not None:
        statement = statement.where(Question.question_type == question_type)
    if difficulty is not None:
        statement = statement.where(Question.difficulty == difficulty)
    if knowledge_point_id is not None:
        statement = statement.join(
            QuestionKnowledgePoint,
            QuestionKnowledgePoint.question_id == Question.id,
        ).where(QuestionKnowledgePoint.knowledge_point_id == knowledge_point_id)
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
                select(QuestionKnowledgePoint.knowledge_point_id)
                .where(
                    QuestionKnowledgePoint.question_id == question_id,
                )
                .order_by(QuestionKnowledgePoint.sort_order, QuestionKnowledgePoint.knowledge_point_id)
            )
        )
        .scalars()
        .all()
    )
    if not knowledge_point_ids:
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
    question.stem_md = question.question_text
    question.analysis_md = question.explanation
    question.answer_data = {
        "kind": question.question_type,
        "value": (
            [item.strip() for item in (question.correct_answer or "").split(",") if item.strip()]
            if question.question_type in {"single_choice", "multiple_choice"}
            else question.correct_answer or ""
        ),
    }
    question.difficulty = question.difficulty or "unspecified"

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


async def update_canonical_question(
    session: AsyncSession,
    question_id: uuid.UUID,
    payload: QuestionPatch,
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
    current_options = current.options
    current_answer = current.answer_data
    current_sources = [
        QuestionSourceCreate(
            source_type=source.source_type,
            source_title=source.source_title or source.source_name,
            source_ref=source.source_ref,
            source_url=source.source_url,
            source_note=source.source_note,
        )
        for source in current.sources
    ]
    values = payload.model_dump(exclude={"version"}, exclude_unset=True)
    try:
        validated = QuestionCreate.model_validate(
            {
                "subject_id": question.subject_id,
                "title": question.title,
                "stem_md": current.stem_md,
                "question_type": question.question_type,
                "options": current_options,
                "answer_data": current_answer,
                "analysis_md": current.analysis_md,
                "difficulty": current.difficulty,
                "knowledge_point_links": [
                    {"knowledge_point_id": value} for value in current.knowledge_point_ids
                ],
                "sources": current_sources,
                **values,
            }
        )
    except ValidationError as error:
        raise QuestionValidationError(str(error)) from error
    await _validate_taxonomy(
        session,
        validated.subject_id,
        [link.knowledge_point_id for link in validated.knowledge_point_links],
    )

    answer_value = validated.answer_data.get("value")
    legacy_answer = ",".join(str(item) for item in answer_value) if isinstance(answer_value, list) else str(answer_value)
    question.subject_id = validated.subject_id
    question.title = validated.title
    question.stem_md = validated.stem_md
    question.question_text = validated.stem_md
    question.question_type = validated.question_type
    question.options = [option.model_dump() for option in validated.options]
    question.answer_data = validated.answer_data
    question.correct_answer = legacy_answer
    question.analysis_md = validated.analysis_md
    question.explanation = validated.analysis_md
    question.difficulty = validated.difficulty

    if "knowledge_point_links" in values:
        await session.execute(
            delete(QuestionKnowledgePoint).where(QuestionKnowledgePoint.question_id == question_id)
        )
        await session.execute(
            delete(KnowledgePointLink).where(
                KnowledgePointLink.target_type == "question",
                KnowledgePointLink.target_id == str(question_id),
            )
        )
        for link in validated.knowledge_point_links:
            session.add(QuestionKnowledgePoint(question_id=question_id, **link.model_dump()))
            session.add(
                KnowledgePointLink(
                    knowledge_point_id=link.knowledge_point_id,
                    target_type="question",
                    target_id=str(question_id),
                )
            )
    if "sources" in values:
        await session.execute(delete(QuestionSource).where(QuestionSource.question_id == question_id))
        for source in validated.sources or []:
            session.add(
                QuestionSource(
                    question_id=question_id,
                    source_type=source.source_type,
                    source_name=source.source_title,
                    source_title=source.source_title,
                    source_ref=source.source_ref,
                    source_url=source.source_url,
                    source_note=source.source_note,
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
