"""PR-10 N+1 evidence: statement count must not grow with active KP count.

Run via the Week 3 scratch guard:

    python3 scripts/week3-scratch-guard.py run --db-name astra_week3_pr10 \
        -- zsh -c 'cd backend && PYTHONPATH=. .venv/bin/python tests/_pr10_n1_evidence.py'
"""

from __future__ import annotations

import asyncio
import uuid

from sqlalchemy import event

from app.utils.scratch_db_safety import require_scratch_database
from app.config import get_settings

require_scratch_database(get_settings().DATABASE_URL)

from app.database import async_session, engine
from app.schemas.question import QuestionDraftCreate
from app.schemas.taxonomy import KnowledgePointCreate, SubjectCreate
from app.services.draft_service import convert_question_draft, create_question_draft
from app.services.kp_analytics_service import get_knowledge_point_analytics
from app.services.taxonomy_service import create_knowledge_point, create_subject


async def _statement_count(session) -> int:
    statements: list[str] = []

    def _capture(conn, cursor, statement, parameters, context, executemany):
        statements.append(statement)

    event.listen(engine.sync_engine, "before_cursor_execute", _capture)
    try:
        await get_knowledge_point_analytics(session)
    finally:
        event.remove(engine.sync_engine, "before_cursor_execute", _capture)
    return len(statements)


async def _add_kp(session, subject) -> None:
    kp = await create_knowledge_point(
        session,
        KnowledgePointCreate(subject_id=subject.id, name=f"n1 {uuid.uuid4().hex[:8]}"),
    )
    draft = await create_question_draft(
        session,
        QuestionDraftCreate(
            subject_id=subject.id,
            question_text=f"n1 question {uuid.uuid4().hex[:8]}?",
            question_type="short_answer",
            correct_answer="a",
            knowledge_point_ids=[kp.id],
        ),
    )
    await convert_question_draft(session, draft.item.id, version=1)


async def main() -> None:
    await engine.dispose(close=False)
    async with async_session() as session:
        async with session.begin():
            subject = await create_subject(
                session, SubjectCreate(name=f"n1 subject {uuid.uuid4().hex[:8]}")
            )
            await _add_kp(session, subject)
            await session.flush()
            small = await _statement_count(session)

            for _ in range(24):
                await _add_kp(session, subject)
            await session.flush()
            large = await _statement_count(session)

            print(
                "PR-10 N+1 evidence: analytics statements for "
                f"1 active KP = {small}, for 25 active KPs = {large}"
            )
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
