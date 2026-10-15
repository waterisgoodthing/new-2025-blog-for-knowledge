#!/usr/bin/env python3
"""PR-11 independent verifier: canonical seed + SQL recomputation of the three answers.

Authored by PR-11-verify (senior-qa-sdet). Does NOT import implementer test
helpers. Seeds canonical rows directly through ORM models, then recomputes each
displayed value with *independent* SQL and compares it to the dashboard service
output. Leaves the seeded rows committed so the API/browser phase can reuse the
same canonical data.

Run from backend/ via the Week 3 scratch guard:

    python3 ../scripts/week3-scratch-guard.py run \
        --db-name astra_week3_pr11_verify \
        -- env PYTHONPATH=. .venv/bin/python \
           ../week3/evidence/sql/pr-11-verify-seed-recompute.py
"""

from __future__ import annotations

import asyncio
import json
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from tempfile import TemporaryDirectory

from sqlalchemy import text
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

import os
import sys

sys.path.insert(0, os.getcwd())

from app.models.attempt import Attempt  # noqa: E402
from app.models.mistake import Mistake  # noqa: E402
from app.models.note import Subject  # noqa: E402
from app.models.question import DraftItem, Question, QuestionKnowledgePoint  # noqa: E402
from app.models.review_item import ReviewItem, ReviewRecord  # noqa: E402
from app.models.taxonomy import KnowledgePoint, KnowledgePointLink  # noqa: E402
from app.services import dashboard_service, practice_service  # noqa: E402

SUBJECT_PREFIX = "PR11V"
ADMIN_USERNAME = "pr11-verify-admin"
ADMIN_PASSWORD = "pr11-verify-pass-123"

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
    subject = Subject(name=f"{SUBJECT_PREFIX} Subject")
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

    async def mistake(q, label: str):
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
            reason_category="concept",
            status="active",
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

    # --- K1 Alpha: 2 wrong attempts -> wrong_rate 1.0; 2 lapses; 1 due --------
    q1 = await question("Alpha", "q1")
    await attempt(q1, correct=False, days_ago=10)
    await attempt(q1, correct=False, days_ago=9)
    m1 = await mistake(q1, "m1")
    link("Alpha", m1)
    ri1 = await review_item(m1, state="active", next_at=NOW - timedelta(hours=2))
    record(ri1, rating=1, reviewed_at=NOW - timedelta(days=8), new_state="active")
    record(ri1, rating=1, reviewed_at=NOW - timedelta(days=6), new_state="active")

    # --- K2 Beta: 1 wrong / 2 attempts -> wrong_rate 0.5 ---------------------
    q2 = await question("Beta", "q2")
    await attempt(q2, correct=False, days_ago=10)
    await attempt(q2, correct=True, days_ago=9)
    m2 = await mistake(q2, "m2")
    link("Beta", m2)
    ri2 = await review_item(m2, state="active", next_at=NOW + timedelta(days=5))

    # --- K3 Gamma: no wrong; 1 due review -----------------------------------
    q3 = await question("Gamma", "q3")
    m3 = await mistake(q3, "m3")
    link("Gamma", m3)
    ri3 = await review_item(m3, state="active", next_at=NOW - timedelta(hours=1))

    # --- K4 Delta: zero metrics (excluded from top3) ------------------------
    q4 = await question("Delta", "q4")

    # --- q5 recent practice attempt (within 168h) -> practice-excluded ------
    q5 = await question("Gamma", "q5-recent")
    await attempt(q5, correct=True, days_ago=0.5)

    # --- q6 mastered linked mistake -> practice-excluded, recently mastered -
    q6 = await question("Alpha", "q6-mastered")
    m6 = await mistake(q6, "m6")
    link("Alpha", m6)
    ri6 = await review_item(m6, state="mastered", next_at=NOW + timedelta(days=30))
    record(ri6, rating=5, reviewed_at=NOW - timedelta(minutes=30), new_state="mastered")

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
    return {"subject_id": subject.id, "k1": kps["Alpha"].id, "k2": kps["Beta"].id,
            "k3": kps["Gamma"].id, "k4": kps["Delta"].id}


async def sql_due_reviews(session) -> int:
    return int(
        (
            await session.execute(
                text(
                    "SELECT count(*) FROM review_items "
                    "WHERE state = 'active' AND next_review_at <= now()"
                )
            )
        ).scalar_one()
    )


async def sql_practice_returned(session) -> dict:
    # Independent restatement of W3-D05 (PR-13) eligibility.
    row = (
        await session.execute(
            text(
                """
                WITH qkp AS (
                    SELECT q.id AS qid, qkp.knowledge_point_id AS kp
                    FROM questions q
                    JOIN question_knowledge_points qkp ON qkp.question_id = q.id
                    JOIN knowledge_points kp
                      ON kp.id = qkp.knowledge_point_id AND kp.status = 'active'
                    WHERE q.status = 'active'
                ),
                recent AS (
                    SELECT DISTINCT question_id
                    FROM attempts
                    WHERE context_type = 'practice'
                      AND submitted_at >= now() - interval '168 hours'
                      AND submitted_at <= now()
                ),
                mastered AS (
                    SELECT DISTINCT m.question_id
                    FROM mistakes m
                    JOIN review_items ri ON ri.mistake_id = m.id
                    WHERE ri.state = 'mastered'
                )
                SELECT count(DISTINCT qid) FROM qkp
                WHERE qid NOT IN (SELECT question_id FROM recent)
                  AND qid NOT IN (SELECT question_id FROM mastered)
                """
            )
        )
    ).scalar_one()
    eligible = int(row)
    return {"eligible": eligible, "returned": min(eligible, 3)}


async def sql_weak_order(session) -> list[dict]:
    rows = (
        await session.execute(
            text(
                """
                WITH attempt_agg AS (
                    SELECT qkp.knowledge_point_id AS kp,
                           count(a.id) AS attempts,
                           count(*) FILTER (WHERE a.is_correct IS FALSE) AS wrong
                    FROM question_knowledge_points qkp
                    JOIN attempts a ON a.question_id = qkp.question_id
                    JOIN questions q ON q.id = qkp.question_id
                    WHERE a.context_type = 'practice' AND q.status = 'active'
                    GROUP BY qkp.knowledge_point_id
                ),
                review_link AS (
                    SELECT kpl.knowledge_point_id AS kp, ri.id AS ri_id,
                           ri.state AS ri_state, ri.next_review_at AS next_at,
                           rr.id AS rr_id, rr.rating AS rating
                    FROM knowledge_point_links kpl
                    JOIN mistakes m
                      ON kpl.target_type = 'mistake' AND kpl.target_id = m.id::text
                    JOIN review_items ri ON ri.mistake_id = m.id
                    JOIN questions q ON q.id = m.question_id
                    LEFT JOIN review_records rr ON rr.review_item_id = ri.id
                    WHERE m.status = 'active' AND q.status = 'active'
                ),
                review_agg AS (
                    SELECT kp, count(rr_id) AS reviews,
                           count(*) FILTER (WHERE rr_id IS NOT NULL AND rating <= 2) AS lapses
                    FROM review_link GROUP BY kp
                ),
                due_agg AS (
                    SELECT kp, count(DISTINCT ri_id) AS due
                    FROM review_link
                    WHERE ri_state = 'active' AND next_at <= now()
                    GROUP BY kp
                )
                SELECT kp.id,
                       kp.name,
                       coalesce(a.attempts, 0) AS attempts,
                       coalesce(a.wrong, 0) AS wrong,
                       coalesce(r.lapses, 0) AS lapses,
                       coalesce(d.due, 0) AS due
                FROM knowledge_points kp
                LEFT JOIN attempt_agg a ON a.kp = kp.id
                LEFT JOIN review_agg r ON r.kp = kp.id
                LEFT JOIN due_agg d ON d.kp = kp.id
                WHERE kp.status = 'active'
                ORDER BY
                    (CASE WHEN coalesce(a.attempts,0) = 0 THEN 0
                          ELSE coalesce(a.wrong,0)::float / a.attempts END) DESC,
                    coalesce(r.lapses, 0) DESC,
                    coalesce(d.due, 0) DESC,
                    kp.id ASC
                LIMIT 3
                """
            )
        )
    ).all()
    out = []
    for kp_id, name, attempts, wrong, lapses, due in rows:
        wrong_rate = 0.0 if attempts == 0 else wrong / attempts
        out.append(
            {
                "knowledge_point_id": int(kp_id),
                "name": name,
                "attempt_count": int(attempts),
                "wrong_rate": wrong_rate,
                "lapse_count": int(lapses),
                "due_count": int(due),
            }
        )
    return out


async def main() -> int:
    engine = create_async_engine(os.environ["DATABASE_URL"])
    maker = async_sessionmaker(engine, expire_on_commit=False)
    try:
        async with maker() as session:
            await cleanup(session)
            await session.commit()
            ids = await seed(session)
            print(f"SEED ok subject={ids['subject_id']}")

        async with maker() as session:
            expected_due = await sql_due_reviews(session)
            expected_practice = await sql_practice_returned(session)
            expected_weak = await sql_weak_order(session)

        tmp = TemporaryDirectory()
        async with maker() as session:
            summary = await dashboard_service.get_dashboard_summary(
                session, upload_root=Path(tmp.name), now=datetime.now(timezone.utc)
            )
        tmp.cleanup()

        actual_weak = [
            {
                "knowledge_point_id": w.knowledge_point_id,
                "name": w.name,
                "attempt_count": w.attempt_count,
                "wrong_rate": w.wrong_rate,
                "lapse_count": w.lapse_count,
                "due_count": w.due_count,
            }
            for w in summary.weak_top3
        ]

        checks = {
            "review_today_count": summary.review_today_count == expected_due,
            "practice_today_count": summary.practice_today_count
            == expected_practice["returned"],
            "weak_top3": actual_weak == expected_weak,
        }
        result = {
            "expected": {
                "review_today_count": expected_due,
                "practice_today_count": expected_practice,
                "weak_top3": expected_weak,
            },
            "service": {
                "review_today_count": summary.review_today_count,
                "practice_today_count": summary.practice_today_count,
                "weak_top3": actual_weak,
                "recently_mastered_4": [
                    {"review_item_id": str(i.review_item_id), "mistake_id": str(i.mistake_id)}
                    for i in summary.recently_mastered_4
                ],
                "today_first_action": summary.today_first_action.model_dump(),
            },
            "checks": checks,
            "all_pass": all(checks.values()),
        }
        print("RESULT_JSON " + json.dumps(result, ensure_ascii=False, default=str))
        return 0 if result["all_pass"] else 1
    finally:
        await engine.dispose()


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
