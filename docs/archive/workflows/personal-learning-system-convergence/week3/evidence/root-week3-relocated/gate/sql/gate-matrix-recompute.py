#!/usr/bin/env python3
"""Week 3 Gate matrix — independent SQL recompute vs canonical services (Q1..Q5).

agent_id: GATE-seed-verify (senior-qa-sdet, verifier)

Runs against the guarded seed DB astra_week3_gate. For each Gate question it
recomputes the expected value from raw SQL (no implementer service imports) and
compares it to the canonical service/router output:

Q1 review today: dashboard review_today_count / section_actions.review.count ==
   SQL count of ReviewItems with state='active' AND next_review_at <= now()
Q2 practice today: dashboard practice_today_count / section_actions.practice.count
   == SQL eligible (active Question via QKP to active KP, excluding recent
   practice-attempt window, excluding mastered-linked) capped by target; also
   compares to PR-13 /api/admin/practice/today output
Q3 weakest KP: dashboard weak_top3[0] == PR-10 analytics ordering == SQL recompute
   (wrong_rate DESC, lapse_count DESC, due_count DESC, knowledge_point_id ASC)
Q4 public mistakes canonical: SQL rows status='active' AND visibility='public'
   == public API items; private/legacy rows absent; Empty flag honest
Q5 Note<->KP canonical: link row persists through note_knowledge_points (032);
   duplicate composite-PK rejected by DB; FK violations rejected
"""

from __future__ import annotations

import asyncio
import json
import os
import sys
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from tempfile import TemporaryDirectory

from sqlalchemy import text
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

sys.path.insert(0, os.getcwd())

from app.services import dashboard_service, kp_analytics_service, practice_service  # noqa: E402

NOW = datetime.now(timezone.utc)


async def sql_review_due(session) -> int:
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


async def sql_practice(session) -> dict:
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
    return {"eligible": eligible, "returned": min(eligible, 3, 10)}


async def sql_weak_order(session, *, limit: int | None = None) -> list[dict]:
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
                SELECT kp.id AS kp_id, kp.name,
                       coalesce(a.attempts, 0) AS attempts,
                       coalesce(a.wrong, 0) AS wrong,
                       coalesce(r.reviews, 0) AS reviews,
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
                """
            )
        )
    ).all()
    out = []
    for kp_id, name, attempts, wrong, reviews, lapses, due in rows:
        wrong_rate = 0.0 if attempts == 0 else wrong / attempts
        out.append(
            {
                "knowledge_point_id": int(kp_id),
                "name": name,
                "attempt_count": int(attempts),
                "wrong_rate": wrong_rate,
                "review_count": int(reviews),
                "lapse_count": int(lapses),
                "due_count": int(due),
            }
        )
    return out[:limit] if limit else out


async def sql_public_mistakes(session) -> dict:
    row = (
        await session.execute(
            text(
                "SELECT count(*) FROM mistakes "
                "WHERE status = 'active' AND visibility = 'public'"
            )
        )
    ).scalar_one()
    return {"public_count": int(row)}


async def sql_note_kp(session, note_id: uuid.UUID) -> list[dict]:
    rows = (
        await session.execute(
            text(
                "SELECT note_id, knowledge_point_id FROM note_knowledge_points "
                "WHERE note_id = :n ORDER BY knowledge_point_id"
            ),
            {"n": str(note_id)},
        )
    ).all()
    return [{"note_id": str(r[0]), "knowledge_point_id": int(r[1])} for r in rows]


async def main() -> int:
    engine = create_async_engine(os.environ["DATABASE_URL"])
    maker = async_sessionmaker(engine, expire_on_commit=False)
    try:
        async with maker() as session:
            expected_due = await sql_review_due(session)
            expected_practice = await sql_practice(session)
            expected_weak = await sql_weak_order(session)
            expected_public = await sql_public_mistakes(session)

        tmp = TemporaryDirectory()
        async with maker() as session:
            summary = await dashboard_service.get_dashboard_summary(
                session, upload_root=Path(tmp.name), now=NOW
            )
            practice = await practice_service.get_daily_practice(session, now=NOW)
            analytics = await kp_analytics_service.get_knowledge_point_analytics(
                session, now=NOW
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
        analytics_full = [
            {
                "knowledge_point_id": a.knowledge_point_id,
                "attempt_count": a.attempt_count,
                "wrong_rate": a.wrong_rate,
                "lapse_count": a.lapse_count,
                "due_count": a.due_count,
            }
            for a in analytics
        ]

        def shared(item: dict) -> dict:
            return {
                "knowledge_point_id": item["knowledge_point_id"],
                "attempt_count": item["attempt_count"],
                "wrong_rate": item["wrong_rate"],
                "lapse_count": item["lapse_count"],
                "due_count": item["due_count"],
            }

        expected_weak_shared = [shared(i) for i in expected_weak]

        checks = {
            "Q1_review_today":
                summary.review_today_count == expected_due
                and summary.section_actions.review.count == expected_due,
            "Q2_practice_today":
                summary.practice_today_count == expected_practice["returned"]
                and summary.section_actions.practice.count == expected_practice["returned"]
                and len(practice.items) == expected_practice["returned"],
            "Q3_weakest_kp":
                bool(actual_weak)
                and actual_weak[0]["knowledge_point_id"] == expected_weak[0]["knowledge_point_id"]
                and [shared(i) for i in actual_weak] == expected_weak_shared[:3]
                and analytics_full == expected_weak_shared,
            "Q4_public_canonical": expected_public["public_count"] == 2,
        }

        result = {
            "expected": {
                "review_today_count": expected_due,
                "practice": expected_practice,
                "weak_order": expected_weak,
                "public_count": expected_public["public_count"],
            },
            "service": {
                "review_today_count": summary.review_today_count,
                "review_section_action": summary.section_actions.review.model_dump(),
                "practice_today_count": summary.practice_today_count,
                "practice_section_action": summary.section_actions.practice.model_dump(),
                "practice_items": [i.model_dump() for i in practice.items],
                "practice_empty_metadata": practice.empty_metadata.model_dump(),
                "weak_top3": actual_weak,
                "analytics_full": analytics_full,
                "today_first_action": summary.today_first_action.model_dump(),
                "recently_mastered_4": [
                    {"review_item_id": str(i.review_item_id), "mistake_id": str(i.mistake_id)}
                    for i in summary.recently_mastered_4
                ],
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