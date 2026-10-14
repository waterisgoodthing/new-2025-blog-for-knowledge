"""PR-10 verification: capture the actual SQL emitted by the analytics query.

Shows that the service issues exactly ONE statement regardless of active KP
count, and prints that statement for independent reading.

Run via the Week 3 guard:

    python3 scripts/week3-scratch-guard.py run --db-name astra_week3_pr10_verify \
        -- backend/.venv/bin/python docs/workflows/personal-learning-system-convergence/week3/evidence/sql/pr-10-verify-analytics-query.py
"""

from __future__ import annotations

import asyncio
import sys
import uuid

sys.path.insert(0, "backend")

from sqlalchemy import event  # noqa: E402

from app.database import async_session, engine  # noqa: E402
from app.schemas.question import QuestionDraftCreate  # noqa: E402
from app.schemas.taxonomy import KnowledgePointCreate, SubjectCreate  # noqa: E402
from app.services.draft_service import (  # noqa: E402
    convert_question_draft,
    create_question_draft,
)
from app.services.kp_analytics_service import (  # noqa: E402
    get_knowledge_point_analytics,
)
from app.services.taxonomy_service import (  # noqa: E402
    create_knowledge_point,
    create_subject,
)


async def _capture(session):
    seen: list[str] = []

    def _cap(conn, cursor, statement, parameters, context, executemany):
        seen.append(statement)

    event.listen(engine.sync_engine, "before_cursor_execute", _cap)
    try:
        await get_knowledge_point_analytics(session)
    finally:
        event.remove(engine.sync_engine, "before_cursor_execute", _cap)
    return seen


async def _add_kp(session, subject) -> None:
    kp = await create_knowledge_point(
        session,
        KnowledgePointCreate(subject_id=subject.id, name=f"sql-{uuid.uuid4().hex[:8]}"),
    )
    draft = await create_question_draft(
        session,
        QuestionDraftCreate(
            subject_id=subject.id,
            question_text=f"sql question {uuid.uuid4().hex[:8]}?",
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
                session, SubjectCreate(name=f"sql-subject-{uuid.uuid4().hex[:8]}")
            )
            await _add_kp(session, subject)
            await session.flush()
            first = await _capture(session)

            for _ in range(5):
                await _add_kp(session, subject)
            await session.flush()
            second = await _capture(session)

            print(f"N=1 active KP  -> analytics statements = {len(first)}")
            print(f"N=6 active KPs -> analytics statements = {len(second)}")
            print("--- captured statement (N=1) ---")
            for stmt in first:
                print(stmt.strip())
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
