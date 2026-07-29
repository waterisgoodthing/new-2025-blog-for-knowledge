import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.attempt import Attempt
from app.models.question import Question
from app.schemas.mistake import MistakeDraftCreate
from app.services import mistake_service


class AttemptError(Exception):
    pass


class AttemptNotFound(AttemptError):
    pass


class AttemptConflict(AttemptError):
    pass


def _is_correct(question: Question, submitted_answer: str) -> bool:
    answer = question.answer_data or {"value": question.correct_answer}
    expected = answer.get("value")
    if isinstance(expected, bool):
        return submitted_answer.strip().lower() in ({"true", "1", "正确"} if expected else {"false", "0", "错误"})
    if isinstance(expected, list):
        submitted = {item.strip() for item in submitted_answer.split(",") if item.strip()}
        return submitted == {str(item).strip() for item in expected}
    return submitted_answer.strip() == str(expected or "").strip()


async def submit_attempt(session: AsyncSession, question_id: uuid.UUID, *, submitted_answer: str, created_by=None) -> Attempt:
    question = await session.get(Question, question_id)
    if question is None or question.status != "active":
        raise AttemptNotFound("Active question not found")
    attempt = Attempt(question_id=question.id, submitted_answer=submitted_answer.strip(), is_correct=_is_correct(question, submitted_answer), created_by=created_by)
    session.add(attempt)
    await session.flush()
    if not attempt.is_correct:
        await create_mistake_draft_for_attempt(session, attempt.id, created_by=created_by)
    await session.refresh(attempt)
    return attempt


async def create_mistake_draft_for_attempt(session: AsyncSession, attempt_id: uuid.UUID, *, created_by=None):
    attempt = await session.get(Attempt, attempt_id)
    if attempt is None:
        raise AttemptNotFound("Attempt not found")
    if attempt.is_correct:
        raise AttemptConflict("Correct attempts do not create mistake drafts")
    if attempt.mistake_draft_item_id:
        return await mistake_service.get_mistake_draft(session, attempt.mistake_draft_item_id)
    question = await session.get(Question, attempt.question_id)
    if question is None:
        raise AttemptNotFound("Attempt question not found")
    record = await mistake_service.create_mistake_draft(
        session,
        MistakeDraftCreate(
            question_id=question.id,
            my_answer=attempt.submitted_answer,
            difficulty=None if question.difficulty == "unspecified" else question.difficulty,
        ),
        created_by=created_by,
        attempt_id=attempt.id,
    )
    attempt.mistake_draft_item_id = record.item.id
    await session.flush()
    return record
