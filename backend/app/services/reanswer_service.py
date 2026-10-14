"""Re-answer evaluation service (R02/D5).

Pure judgment functions plus the review-context attempt submission.
TRIAGE (documented, reviewer-scrutinized):
- verdict correct -> recommendation 4 (success without claiming perfect recall;
  rating=5 stays a user-confirmed mastery signal per D2).
- verdict incorrect -> recommendation 2 (mild lapse档 per D2; the machine may be
  wrong, so it never imposes the harshest 0/1 lapse; the user can downgrade).
- verdict needs_human -> recommendation None (no machine basis; returning a
  number would be unverified output treated as fact).
- needs_human attempts store is_correct=False ("not demonstrated correct"),
  never create mistake drafts (the mistake already exists), and are excluded
  from practice stats by context_type (D4/D7).
"""

import re
import unicodedata
import uuid
from dataclasses import dataclass
from typing import Literal

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.attempt import Attempt
from app.models.question import Question
from app.services.attempt_service import AttemptConflict, AttemptNotFound

Verdict = Literal["correct", "incorrect", "needs_human"]

_TRUE_TOKENS = {"true", "1", "正确", "对", "t", "yes"}
_FALSE_TOKENS = {"false", "0", "错误", "错", "f", "no"}
_SPLIT_RE = re.compile(r"[,，、;；\s]+")
_EDGE_PUNCT_RE = re.compile(r"^[，。,.!！?？;；:：、\"'“”‘’()（）\[\]【】]+|[，。,.!！?？;；:：、\"'“”‘’()（）\[\]【】]+$")
_WS_RE = re.compile(r"\s+")


@dataclass(frozen=True)
class Evaluation:
    verdict: Verdict
    recommendation: int | None


def _normalize_key(raw: str) -> str:
    return raw.strip().upper()


def _normalize_text(raw: str) -> str:
    # NFKC folds fullwidth forms (＞→>, Ｘ→x, ，→,) for CJK input; lowercase;
    # drop ALL whitespace (interior spaces are insignificant in short answers);
    # strip EDGE punctuation only — interior "1,000"/"it's"/"a-b" stay distinct
    # (M1: never over-match interior punctuation into `correct`).
    folded = unicodedata.normalize("NFKC", raw.strip().lower())
    nows = _WS_RE.sub("", folded)
    return _EDGE_PUNCT_RE.sub("", nows)


def _split_keys(raw: str) -> set[str]:
    return {_normalize_key(part) for part in _SPLIT_RE.split(raw) if part.strip()}


def evaluate_answer(question_type: str, answer_data: dict | None, submitted_answer: str) -> Evaluation:
    """Judge a re-answer WITHOUT cross-type bare string equality (D5).

    - single_choice / multiple_choice / true_false: automatic.
    - short_answer: semi-automatic ONLY when answer_data carries an explicit
      machine-matchable value; otherwise needs_human.
    - essay and anything else: needs_human (reference answer shown, user rates).
    """
    submitted = (submitted_answer or "").strip()
    if not submitted:
        return Evaluation(verdict="needs_human", recommendation=None)
    answer = answer_data or {}
    expected = answer.get("value")

    if question_type == "single_choice":
        # Canonical contract (QuestionCreate): value is a one-element key list.
        if not isinstance(expected, list) or len(expected) != 1 or not str(expected[0]).strip():
            return Evaluation(verdict="needs_human", recommendation=None)
        ok = _normalize_key(submitted) == _normalize_key(str(expected[0]))
        return Evaluation(verdict="correct" if ok else "incorrect", recommendation=4 if ok else 2)

    if question_type == "multiple_choice":
        # Canonical contract: value is a non-empty key list; exact set match.
        if not isinstance(expected, list) or not expected:
            return Evaluation(verdict="needs_human", recommendation=None)
        wanted = {_normalize_key(str(item)) for item in expected if str(item).strip()}
        if not wanted:
            return Evaluation(verdict="needs_human", recommendation=None)
        ok = _split_keys(submitted) == wanted
        return Evaluation(verdict="correct" if ok else "incorrect", recommendation=4 if ok else 2)

    if question_type == "true_false":
        token = submitted.strip().lower()
        if isinstance(expected, bool):
            wanted = _TRUE_TOKENS if expected else _FALSE_TOKENS
            if token not in _TRUE_TOKENS | _FALSE_TOKENS:
                return Evaluation(verdict="needs_human", recommendation=None)
            ok = token in wanted
            return Evaluation(verdict="correct" if ok else "incorrect", recommendation=4 if ok else 2)
        return Evaluation(verdict="needs_human", recommendation=None)

    if question_type == "short_answer":
        if not isinstance(expected, str) or not expected.strip():
            return Evaluation(verdict="needs_human", recommendation=None)
        ok = _normalize_text(submitted) == _normalize_text(expected)
        return Evaluation(verdict="correct" if ok else "incorrect", recommendation=4 if ok else 2)

    return Evaluation(verdict="needs_human", recommendation=None)


async def submit_reanswer_attempt(
    session: AsyncSession,
    question_id: uuid.UUID,
    *,
    submitted_answer: str,
    created_by=None,
) -> tuple[Attempt, Evaluation]:
    """Submit a re-answer attempt (context_type='review').

    Never creates mistake drafts: the re-answered mistake already exists.
    """
    question = await session.get(Question, question_id)
    if question is None or question.status != "active":
        raise AttemptNotFound("Active question not found")
    cleaned = submitted_answer.strip()
    if not cleaned:
        raise AttemptConflict("submitted_answer must not be blank")
    evaluation = evaluate_answer(question.question_type, question.answer_data, cleaned)
    attempt = Attempt(
        question_id=question.id,
        submitted_answer=cleaned,
        is_correct=evaluation.verdict == "correct",
        context_type="review",
        created_by=created_by,
    )
    session.add(attempt)
    await session.flush()
    await session.refresh(attempt)
    return attempt, evaluation
