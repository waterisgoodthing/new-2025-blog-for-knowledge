#!/usr/bin/env python3
"""Week 3 Gate seed — canonical inventory per week3/README.md §5.

agent_id: GATE-seed-verify (senior-qa-sdet, verifier)

Seeds a fresh guarded scratch DB (astra_week3_gate) with:

- two+ KnowledgePoints with deliberately different weakness histories
  (A weak/high wrong_rate; B strong/low wrong_rate; C/D tied for tie-breaker)
- active, archived, recently attempted and eligible Questions
- due, future and mastered ReviewItems with ReviewRecords
- public and private canonical Mistakes plus legacy Note mistakes (frozen path)
- a canonical Note linked to a KnowledgePoint through migration 032

Leaves rows committed so API/browser phases reuse the same canonical data.
Does NOT import implementer test helpers.
"""

from __future__ import annotations

import asyncio
import json
import os
import sys
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

from sqlalchemy import text
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

sys.path.insert(0, os.getcwd())

from app.models.attempt import Attempt  # noqa: E402
from app.models.mistake import Mistake  # noqa: E402
from app.models.note import Note, Subject  # noqa: E402
from app.models.note_knowledge_point import NoteKnowledgePoint  # noqa: E402
from app.models.question import DraftItem, Question, QuestionKnowledgePoint  # noqa: E402
from app.models.review_item import ReviewItem, ReviewRecord  # noqa: E402
from app.models.taxonomy import KnowledgePoint, KnowledgePointLink  # noqa: E402

SUBJECT_PREFIX = "GATE"
ADMIN_USERNAME = "gate-admin"
ADMIN_PASSWORD = "gate-admin-pass-123"

NOW = datetime.now(timezone.utc)


async def cleanup(session) -> None:
    subj = "(SELECT id FROM subjects WHERE name LIKE :p)"
    statements = [
        f"DELETE FROM review_records WHERE review_item_id IN ("
        f"SELECT ri.id FROM review_items ri JOIN mistakes m ON ri.mistake_id = m.id "
        f"WHERE m.subject_id IN {subj})",
        f"DELETE FROM review_items WHERE mistake_id IN "
        f"(SELECT id FROM mistakes WHERE subject_id IN {subj})",
        f"DELETE FROM knowledge_point_links WHERE knowledge_point_id IN "
        f"(SELECT id FROM knowledge_points WHERE subject_id IN {subj})",
        f"DELETE FROM note_knowledge_points WHERE note_id IN "
        f"(SELECT id FROM notes WHERE title LIKE :p)",
        "DELETE FROM notes WHERE title LIKE :p",
        f"DELETE FROM mistakes WHERE subject_id IN {subj}",
        f"DELETE FROM draft_items WHERE id IN "
        f"(SELECT source_draft_item_id FROM mistakes WHERE subject_id IN {subj})",
        f"DELETE FROM attempts WHERE question_id IN "
        f"(SELECT id FROM questions WHERE subject_id IN {subj})",
        f"DELETE FROM question_knowledge_points WHERE question_id IN "
        f"(SELECT id FROM questions WHERE subject_id IN {subj})",
        f"DELETE FROM questions WHERE subject_id IN {subj}",
        f"DELETE FROM knowledge_points WHERE subject_id IN {subj}",
        "DELETE FROM subjects WHERE name LIKE :p",
        "DELETE FROM users WHERE username = :u",
    ]
    for stmt in statements:
        await session.execute(text(stmt), {"p": f"{SUBJECT_PREFIX}%", "u": ADMIN_USERNAME})
    await session.commit()


async def seed(session) -> dict:
    subject = Subject(name=f"{SUBJECT_PREFIX} Gate Subject")
    session.add(subject)
    await session.flush()

    kps = {}
    for key in ("Alpha", "Beta", "Gamma", "Delta"):
        kp = KnowledgePoint(subject_id=subject.id, name=f"{SUBJECT_PREFIX} {key}")
        session.add(kp)
        await session.flush()
        kps[key] = kp

    async def question(kp_key: str, label: str, *, status: str = "active"):
        q = Question(
            subject_id=subject.id,
            title=f"{SUBJECT_PREFIX} {label}",
            stem_md="",
            question_text=f"{SUBJECT_PREFIX} question {label}?",
            question_type="short_answer",
            correct_answer="A",
            status=status,
        )
        session.add(q)
        await session.flush()
        session.add(
            QuestionKnowledgePoint(question_id=q.id, knowledge_point_id=kps[kp_key].id)
        )
        await session.flush()
        return q

    async def attempt(q, *, correct: bool, days_ago: float):
        a = Attempt(
            question_id=q.id,
            submitted_answer="x",
            is_correct=correct,
            context_type="practice",
            submitted_at=NOW - timedelta(days=days_ago),
        )
        session.add(a)
        await session.flush()
        return a

    async def mistake(q, label: str, *, visibility: str = "private", status: str = "active"):
        item = DraftItem(
            draft_type="mistake",
            source_type="question",
            source_id=str(q.id),
            status="pending",
        )
        session.add(item)
        await session.flush()
        m = Mistake(
            source_draft_item_id=item.id,
            question_id=q.id,
            subject_id=subject.id,
            title=f"{SUBJECT_PREFIX} mistake {label}",
            question_text=f"{SUBJECT_PREFIX} mistake text {label}",
            my_answer=f"{SUBJECT_PREFIX}PRIVATE_{label}_secret",
            correct_answer="A",
            analysis=f"{SUBJECT_PREFIX} analysis {label}",
            reason_category="concept",
            mistake_reason=f"{SUBJECT_PREFIX} reason {label}",
            difficulty="medium",
            status=status,
            visibility=visibility,
        )
        session.add(m)
        await session.flush()
        return m

    def link(kp_key: str, m: Mistake):
        session.add(
            KnowledgePointLink(
                knowledge_point_id=kps[kp_key].id,
                target_type="mistake",
                target_id=str(m.id),
            )
        )

    async def review_item(m, *, state: str, next_at: datetime):
        ri = ReviewItem(
            target_type="mistake",
            target_id=str(m.id),
            mistake_id=m.id,
            state=state,
            interval_days=0,
            repetitions=0,
            next_review_at=next_at,
        )
        session.add(ri)
        await session.flush()
        return ri

    def record(ri, *, rating: int, reviewed_at: datetime, new_state: str):
        session.add(
            ReviewRecord(
                review_item_id=ri.id,
                rating=rating,
                reviewed_at=reviewed_at,
                previous_interval_days=0,
                next_interval_days=3,
                previous_next_review_at=reviewed_at - timedelta(days=1),
                next_review_at=reviewed_at + timedelta(days=3),
                previous_state="active",
                new_state=new_state,
            )
        )

    # === KP Alpha (weak, high wrong_rate) ===
    q_a1 = await question("Alpha", "q-a1")          # eligible practice
    await attempt(q_a1, correct=False, days_ago=10)
    await attempt(q_a1, correct=False, days_ago=9)
    m_pub1 = await mistake(q_a1, "m-pub1", visibility="public")
    link("Alpha", m_pub1)
    ri_due1 = await review_item(m_pub1, state="active", next_at=NOW - timedelta(hours=2))
    record(ri_due1, rating=1, reviewed_at=NOW - timedelta(days=8), new_state="active")
    record(ri_due1, rating=2, reviewed_at=NOW - timedelta(days=6), new_state="active")

    q_a2 = await question("Alpha", "q-a2")          # eligible practice
    await attempt(q_a2, correct=False, days_ago=11)
    await attempt(q_a2, correct=False, days_ago=10)
    await attempt(q_a2, correct=True, days_ago=9)
    m_priv1 = await mistake(q_a2, "m-priv1", visibility="private")
    link("Alpha", m_priv1)
    ri_due2 = await review_item(m_priv1, state="active", next_at=NOW - timedelta(hours=1))
    record(ri_due2, rating=4, reviewed_at=NOW - timedelta(days=3), new_state="active")

    q_archived = await question("Alpha", "q-archived", status="archived")
    await attempt(q_archived, correct=False, days_ago=5)  # must be excluded from analytics
    m_priv_archived = await mistake(q_archived, "m-priv-archived", visibility="private", status="archived")
    link("Alpha", m_priv_archived)
    ri_archived = await review_item(m_priv_archived, state="paused", next_at=NOW + timedelta(days=10))
    record(ri_archived, rating=3, reviewed_at=NOW - timedelta(days=4), new_state="paused")

    # === KP Beta (strong, low wrong_rate) ===
    q_b1 = await question("Beta", "q-b1")           # eligible practice
    for i in range(4):
        await attempt(q_b1, correct=True, days_ago=10 + i)
    await attempt(q_b1, correct=False, days_ago=14)
    m_pub2 = await mistake(q_b1, "m-pub2", visibility="public")
    link("Beta", m_pub2)
    ri_future = await review_item(m_pub2, state="active", next_at=NOW + timedelta(days=5))
    record(ri_future, rating=4, reviewed_at=NOW - timedelta(days=2), new_state="active")

    # === KP Gamma (0.5 wrong_rate; tie with Delta) ===
    q_recent = await question("Gamma", "q-recent")  # recently attempted (in-window)
    await attempt(q_recent, correct=False, days_ago=0.2)
    await attempt(q_recent, correct=True, days_ago=0.1)
    m_priv_c = await mistake(q_recent, "m-priv-c", visibility="private")
    link("Gamma", m_priv_c)
    ri_c_future = await review_item(m_priv_c, state="active", next_at=NOW + timedelta(days=7))
    record(ri_c_future, rating=4, reviewed_at=NOW - timedelta(days=1), new_state="active")

    q_mastered = await question("Gamma", "q-mastered")  # mastered-excluded from practice
    await attempt(q_mastered, correct=False, days_ago=8)
    await attempt(q_mastered, correct=True, days_ago=7)
    m_mastered = await mistake(q_mastered, "m-mastered", visibility="private")
    link("Gamma", m_mastered)
    ri_mastered = await review_item(m_mastered, state="mastered", next_at=NOW + timedelta(days=30))
    record(ri_mastered, rating=5, reviewed_at=NOW - timedelta(minutes=30), new_state="mastered")

    # === KP Delta (0.5 wrong_rate; tie with Gamma, must sort after by id) ===
    q_extra = await question("Delta", "q-extra")    # eligible practice
    await attempt(q_extra, correct=False, days_ago=9)
    await attempt(q_extra, correct=False, days_ago=8)
    await attempt(q_extra, correct=True, days_ago=7)
    await attempt(q_extra, correct=True, days_ago=6)
    m_priv_d = await mistake(q_extra, "m-priv-d", visibility="private")
    link("Delta", m_priv_d)
    ri_d_future = await review_item(m_priv_d, state="active", next_at=NOW + timedelta(days=6))
    record(ri_d_future, rating=4, reviewed_at=NOW - timedelta(days=2), new_state="active")

    # === Legacy Note mistakes (frozen path; must NOT appear in public API) ===
    legacy_rows = [
        ("gate-legacy-mistake-1", "published", False),
        ("gate-legacy-mistake-2", "unpublished", False),
    ]
    for slug, status, hidden in legacy_rows:
        note = Note(
            slug=slug,
            title=f"{SUBJECT_PREFIX} legacy {slug}",
            content="",
            type="mistake",
            status=status,
            hidden=hidden,
            subject="legacy",
            question="legacy q",
            my_answer="legacy private answer",
            correct_answer="L",
            analysis="legacy analysis",
        )
        session.add(note)
    await session.flush()

    # === Canonical Note linked to a KnowledgePoint via migration 032 ===
    canonical_note = Note(
        slug="gate-canonical-note",
        title=f"{SUBJECT_PREFIX} canonical note",
        content="canonical note body",
        type="note",
        status="published",
        hidden=False,
        subject="canonical",
    )
    session.add(canonical_note)
    await session.flush()
    session.add(
        NoteKnowledgePoint(note_id=canonical_note.id, knowledge_point_id=kps["Alpha"].id)
    )

    user_id = uuid.uuid4()
    from app.utils.auth import hash_password

    await session.execute(
        text(
            "INSERT INTO users (id,username,password_hash,is_admin) "
            "VALUES (:id,:u,:p,true)"
        ),
        {"id": user_id, "u": ADMIN_USERNAME, "p": hash_password(ADMIN_PASSWORD)},
    )
    await session.commit()
    return {
        "subject_id": subject.id,
        "kp": {k: v.id for k, v in kps.items()},
        "question": {
            "q_a1": str(q_a1.id),
            "q_a2": str(q_a2.id),
            "q_b1": str(q_b1.id),
            "q_archived": str(q_archived.id),
            "q_recent": str(q_recent.id),
            "q_mastered": str(q_mastered.id),
            "q_extra": str(q_extra.id),
        },
        "mistake": {
            "m_pub1": str(m_pub1.id),
            "m_priv1": str(m_priv1.id),
            "m_pub2": str(m_pub2.id),
            "m_mastered": str(m_mastered.id),
        },
        "review_item": {
            "ri_due1": str(ri_due1.id),
            "ri_due2": str(ri_due2.id),
            "ri_mastered": str(ri_mastered.id),
        },
        "note": {
            "canonical": str(canonical_note.id),
            "legacy_1": "gate-legacy-mistake-1",
            "legacy_2": "gate-legacy-mistake-2",
        },
    }


async def main() -> int:
    engine = create_async_engine(os.environ["DATABASE_URL"])
    maker = async_sessionmaker(engine, expire_on_commit=False)
    try:
        async with maker() as session:
            await cleanup(session)
            ids = await seed(session)
            print("SEED ok " + json.dumps(ids, ensure_ascii=False, default=str))
        return 0
    finally:
        await engine.dispose()


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))