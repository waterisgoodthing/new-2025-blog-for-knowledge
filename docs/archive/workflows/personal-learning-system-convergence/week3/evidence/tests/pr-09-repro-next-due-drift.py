"""PR9F-01 + W3-D10 standalone repro (verifier: PR-09-verify-rework).

Seeds a legacy note with next_review=2026-12-15, runs the wk3 runner, asserts
review_items.next_review_at maps from the source date (not run time). Then
mutates the source title and re-runs to assert source_drift rejection and no
target overwrite (W3-D10).

Run via guard against a scratch DB migrated to 031.
"""

from __future__ import annotations

import asyncio
import json
import os
import uuid
from datetime import date, datetime, timezone

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

SOURCE_NEXT_REVIEW = date(2026, 12, 15)


async def main() -> int:
    engine = create_async_engine(os.environ["DATABASE_URL"])
    session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)()
    results: dict[str, str] = {}
    try:
        await session.execute(text(
            "DO $$ BEGIN "
            "IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname='legacy_note_adapter_runner') THEN "
            "  CREATE ROLE legacy_note_adapter_runner LOGIN; "
            "END IF; "
            "END $$"
        ))
        subject_id = (await session.execute(text(
            "INSERT INTO public.subjects (name, status) VALUES ('pr09-vfy-subj','active') "
            "ON CONFLICT (name) DO UPDATE SET name=EXCLUDED.name RETURNING id"
        ))).scalar_one()
        await session.execute(text(
            "INSERT INTO public.knowledge_points (subject_id, name) VALUES (:sid,'pr09-vfy-kp') "
            "ON CONFLICT DO NOTHING"
        ), {"sid": int(subject_id)})
        await session.commit()

        note_id = uuid.uuid4()
        slug = f"pr09vfy-{note_id.hex[:12]}"
        ai_meta = json.dumps({
            "legacy_question": {"question_type": "true_false", "options": []}
        })
        await session.execute(text(
            "INSERT INTO public.notes "
            "(id,slug,title,content,type,status,hidden,revision,ef,interval,repetitions,"
            "subject,question,my_answer,correct_answer,analysis,knowledge_points,"
            "next_review,ai_metadata) "
            "VALUES (:id,:slug,:title,'c','mistake','published',false,1,2.5,0,0,"
            "'pr09-vfy-subj','Q?','wrong','True','an','pr09-vfy-kp',"
            ":next_review,CAST(:ai_meta AS json))"
        ), {
            "id": note_id, "slug": slug, "title": "original-title",
            "next_review": SOURCE_NEXT_REVIEW, "ai_meta": ai_meta,
        })
        await session.commit()

        from app.services.wk3_mistake_visibility_migration import run_wk3_migration

        report = await run_wk3_migration(session, dry_run=False)
        await session.commit()

        row = (await session.execute(text(
            "SELECT n.next_review AS source_next_review, "
            "       ri.next_review_at AS target_next_due, "
            "       (ri.next_review_at::date = n.next_review) AS next_due_matches_source, "
            "       ri.next_review_at <> now() AS differs_from_run_time "
            "FROM public.notes n "
            "JOIN public.legacy_note_migrations l ON l.source_note_id = n.id "
            "JOIN public.review_items ri ON ri.id = l.target_review_item_id "
            "WHERE n.id = :sid"
        ), {"sid": note_id})).mappings().one_or_none()

        print("PR9F-01 row:", dict(row) if row else None)
        print("PR9F-01 report.next_due_from_source:", report.next_due_from_source)
        print("PR9F-01 report.next_due_default:", report.next_due_default)
        expected = datetime(2026, 12, 15, tzinfo=timezone.utc)
        ok = (
            row is not None
            and row["next_due_matches_source"] is True
            and row["differs_from_run_time"] is True
            and report.next_due_from_source >= 1
        )
        if row is not None:
            nd = row["target_next_due"]
            if isinstance(nd, datetime) and nd.tzinfo is not None:
                ok = ok and nd.astimezone(timezone.utc) == expected
        results["PR9F-01"] = "PASS" if ok else "FAIL"

        await session.execute(text(
            "UPDATE public.notes SET title='changed-title', revision=revision+1 WHERE id=:id"
        ), {"id": note_id})
        await session.commit()
        report2 = await run_wk3_migration(session, dry_run=False)
        await session.commit()

        reasons = [r.get("reason") for r in report2.rejected]
        target_title = (await session.execute(text(
            "SELECT m.title FROM public.mistakes m "
            "JOIN public.legacy_note_migrations l ON l.target_mistake_id = m.id "
            "WHERE l.source_note_id = :sid"
        ), {"sid": note_id})).scalar_one_or_none()
        print("W3-D10 rejected reasons:", reasons)
        print("W3-D10 provenance_match:", report2.provenance_match)
        print("W3-D10 target_title:", target_title)
        d10_ok = (
            "source_drift" in reasons
            and report2.provenance_match is False
            and target_title == "original-title"
        )
        results["W3-D10"] = "PASS" if d10_ok else "FAIL"
    finally:
        await session.rollback()
        await session.close()
        await engine.dispose()

    print("RESULTS:", results)
    return 0 if all(v == "PASS" for v in results.values()) else 1


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
