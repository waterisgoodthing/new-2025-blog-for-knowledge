"""Synthetic LSR-03 positive rehearsal; invoked only through guarded_runner."""

from __future__ import annotations

import asyncio
import os
import uuid
from datetime import datetime, timezone
from urllib.parse import urlsplit, urlunsplit

from sqlalchemy import text
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.services.legacy_note_migration_adapter import migrate


SOURCE = uuid.UUID("11111111-1111-4111-8111-111111111111")
QUESTION = uuid.UUID("22222222-2222-4222-8222-222222222222")
MISTAKE = uuid.UUID("33333333-3333-4333-8333-333333333333")
SCHEDULE_ACTOR = uuid.UUID("66666666-6666-4666-8666-666666666666")
SCHEDULE = SCHEDULE_ACTOR
MAPPED_NEXT_REVIEW_AT = datetime(2026, 8, 26, 0, 0, tzinfo=timezone.utc)


def runner_url(raw: str) -> str:
    parsed = urlsplit(raw)
    return urlunsplit((parsed.scheme, f"legacy_note_adapter_runner@{parsed.hostname}:{parsed.port}", parsed.path, "", ""))


async def main() -> None:
    url = runner_url(os.environ["LSR03_DATABASE_URL"])
    engine = create_async_engine(url)
    maker = async_sessionmaker(engine, expire_on_commit=False)
    sources = (
        (uuid.UUID("88888888-8888-4888-8888-888888888888"), "active", True),
        (uuid.UUID("33333333-3333-4333-8333-333333333334"), "paused", False),
        (uuid.UUID("22222222-2222-4222-8222-222222222223"), "retained", False),
        (uuid.UUID("90000000-0000-4000-8000-000000000019"), "chapter-019", False),
    )
    try:
        for source_id, label, active in sources:
            async with maker() as session:
                payload = (await session.execute(text(
                    "SELECT legacy_migration.canonicalize_legacy_note(:id)"
                ), {"id": source_id})).scalar_one()
                source_hash = (await session.execute(text(
                    "SELECT encode(public.digest(convert_to(legacy_migration.canonicalize_legacy_note(:id)::text,'UTF8'),'sha256'),'hex')"
                ), {"id": source_id})).scalar_one()
                # End the read transaction so migrate can establish its own
                # SERIALIZABLE transaction before any source query.
                await session.commit()
                kwargs = dict(
                    source_note_id=source_id,
                    mapping_version=f"v1-{label}",
                    source_approved_by=SOURCE,
                    source_approved_at=datetime.now(timezone.utc),
                    source_approval_sequence=1,
                    question_conversion_approved_by=QUESTION,
                    question_conversion_approved_at=datetime.now(timezone.utc),
                    question_conversion_sequence=1,
                    mistake_conversion_approved_by=MISTAKE,
                    mistake_conversion_approved_at=datetime.now(timezone.utc),
                    mistake_conversion_sequence=1,
                    canonical_payload=payload,
                    expected_source_hash=source_hash,
                )
                if active:
                    kwargs.update(
                        schedule_approved_by=SCHEDULE_ACTOR,
                        schedule_approved_at=datetime.now(timezone.utc),
                        schedule_approval_sequence=1,
                        mapped_next_review_at=MAPPED_NEXT_REVIEW_AT,
                    )
                result = await migrate(session, **kwargs)
                await session.commit()
                if label == "retained":
                    if result.state != "retained_public_only" or any(
                        value is not None
                        for value in (
                            result.target_question_draft_item_id,
                            result.target_question_draft_id,
                            result.target_question_id,
                            result.target_question_source_id,
                            result.target_mistake_draft_item_id,
                            result.target_mistake_draft_id,
                            result.target_mistake_id,
                            result.target_review_item_id,
                        )
                    ) or result.target_qkp_ids is not None or result.target_projection_ids is not None:
                        raise AssertionError(
                            "retained fixture must be retained_public_only with NULL targets"
                        )
                print(label, result.state, result.idempotent, result.target_qkp_ids, result.target_projection_ids)
        async with maker() as session:
            source_id = sources[0][0]
            payload = (await session.execute(text(
                "SELECT legacy_migration.canonicalize_legacy_note(:id)"
            ), {"id": source_id})).scalar_one()
            source_hash = (await session.execute(text(
                "SELECT encode(public.digest(convert_to(legacy_migration.canonicalize_legacy_note(:id)::text,'UTF8'),'sha256'),'hex')"
            ), {"id": source_id})).scalar_one()
            await session.commit()
            result = await migrate(
                session, source_note_id=source_id, mapping_version="v1-active",
                source_approved_by=SOURCE, source_approved_at=datetime.now(timezone.utc), source_approval_sequence=1,
                question_conversion_approved_by=QUESTION, question_conversion_approved_at=datetime.now(timezone.utc), question_conversion_sequence=1,
                mistake_conversion_approved_by=MISTAKE, mistake_conversion_approved_at=datetime.now(timezone.utc), mistake_conversion_sequence=1,
                canonical_payload=payload, expected_source_hash=source_hash,
                schedule_approved_by=SCHEDULE_ACTOR, schedule_approved_at=datetime.now(timezone.utc), schedule_approval_sequence=1,
                mapped_next_review_at=MAPPED_NEXT_REVIEW_AT,
            )
            await session.commit()
            print("idempotent", result.idempotent)
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
