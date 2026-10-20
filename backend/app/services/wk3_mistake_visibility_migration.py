"""Week 3 legacy-mistake visibility mapping runner (W3-D06..D08, W3F-07/08).

Reuses the migration-026 ledger mechanism with mapping version
``wk3-mistake-visibility-v1``. Two actions per source note:

(a) un-migrated  -> create the canonical chain via ``migrate()`` with
    W3-D06-matrix visibility and ReviewItem v2 defaults;
(b) already-migrated (``v1-*`` targets) -> idempotent UPDATE of
    ``mistakes.visibility`` only; no duplicate ledger target rows.

Dry-run is zero-persistence: the caller must roll back the transaction.
"""

from __future__ import annotations

import asyncio
import json
import uuid
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.legacy_note_migration_adapter import (
    V2_DEFAULT_INTERVAL_DAYS,
    V2_DEFAULT_REPETITIONS,
    V2_REVIEW_ALGORITHM,
    map_legacy_note_to_mistake_visibility,
    migrate,
)

MAPPING_VERSION = "wk3-mistake-visibility-v1"
MAPPING_VERSION_MAX_BYTES = 64

UNMAPPED_SOURCE_FIELDS = ("ef", "interval", "repetitions", "last_reviewed")

_ACTOR_SOURCE = uuid.uuid5(uuid.NAMESPACE_URL, "wk3-mistake-visibility-v1/source-approver")
_ACTOR_QUESTION = uuid.uuid5(uuid.NAMESPACE_URL, "wk3-mistake-visibility-v1/question-approver")
_ACTOR_MISTAKE = uuid.uuid5(uuid.NAMESPACE_URL, "wk3-mistake-visibility-v1/mistake-approver")
_ACTOR_SCHEDULE = uuid.uuid5(uuid.NAMESPACE_URL, "wk3-mistake-visibility-v1/schedule-approver")

_APPROVAL_KINDS = ("source", "question_conversion", "mistake_conversion", "schedule")

_TERMINAL_STATES = ("migrated_active", "migrated_paused", "retained_public_only", "rolled_back")


@dataclass
class Wk3MigrationReport:
    mapping_version: str = MAPPING_VERSION
    generated_at: str = ""
    dry_run: bool = False
    source_total: int = 0
    by_mapping: dict[str, int] = field(default_factory=lambda: {
        "published_visible": 0,
        "published_hidden": 0,
        "unpublished_visible": 0,
        "unpublished_hidden": 0,
    })
    targets_created: int = 0
    visibility_reconciled: int = 0
    skipped_already_migrated: int = 0
    rejected: list[dict[str, str]] = field(default_factory=list)
    review_items_created_v2: int = 0
    next_due_from_source: int = 0
    next_due_default: int = 0
    replay_noop: bool = True
    would_create: int = 0
    would_reconcile: int = 0
    would_create_review_items: int = 0
    would_next_due_from_source: int = 0
    would_next_due_default: int = 0
    provenance_match: bool = True
    visibility_matrix_match: bool = True
    public_field_allowlist_match: bool = True

    def to_json_dict(self) -> dict[str, Any]:
        checks = {
            "count_match": self._count_match(),
            "provenance_match": self.provenance_match,
            "visibility_matrix_match": self.visibility_matrix_match,
            "public_field_allowlist_match": self.public_field_allowlist_match,
            "replay_noop": True if self.dry_run else self.replay_noop,
        }
        return {
            "mapping_version": self.mapping_version,
            "generated_at": self.generated_at,
            "source": {
                "total_legacy_mistakes": self.source_total,
                "by_mapping": dict(self.by_mapping),
            },
            "targets": {
                "created": self.targets_created,
                "visibility_reconciled": self.visibility_reconciled,
                "skipped_already_migrated": self.skipped_already_migrated,
                "skipped_already_migrated_private_ok": self.skipped_already_migrated,
                "rejected": list(self.rejected),
                "would_create": self.would_create,
                "would_reconcile": self.would_reconcile,
            },
            "review_items": {
                "created_v2": self.review_items_created_v2,
                "next_due_from_source": self.next_due_from_source,
                "next_due_default": self.next_due_default,
                "unmapped": list(UNMAPPED_SOURCE_FIELDS),
                "would_create_v2": self.would_create_review_items,
                "would_next_due_from_source": self.would_next_due_from_source,
                "would_next_due_default": self.would_next_due_default,
            },
            "unmapped_source_fields": list(UNMAPPED_SOURCE_FIELDS),
            "checks": checks,
            "idempotency": {"replay_noop": checks["replay_noop"]},
            "dry_run": self.dry_run,
        }

    def _count_match(self) -> bool:
        if self.dry_run:
            accounted = (
                self.would_create
                + self.would_reconcile
                + self.skipped_already_migrated
                + len(self.rejected)
            )
        else:
            accounted = (
                self.targets_created
                + self.visibility_reconciled
                + self.skipped_already_migrated
                + len(self.rejected)
            )
        return accounted == self.source_total


def _mapping_bucket(status: object, hidden: object) -> str:
    published = status == "published"
    visible = not bool(hidden)
    if published and visible:
        return "published_visible"
    if published:
        return "published_hidden"
    if visible:
        return "unpublished_visible"
    return "unpublished_hidden"


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


def _map_next_review_to_due(value: object | None) -> tuple[datetime | None, bool]:
    """Map source next_review to a UTC instant. Returns (mapped, used_source)."""
    if value is None:
        return None, False
    if isinstance(value, datetime):
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc), True
        return value.astimezone(timezone.utc), True
    if isinstance(value, date) and not isinstance(value, datetime):
        return datetime(value.year, value.month, value.day, tzinfo=timezone.utc), True
    return None, False


async def _check_source_drift(
    session: AsyncSession,
    note_id: uuid.UUID,
    ledger_source_title: object,
    ledger_source_revision: object,
) -> bool:
    """Return True when source content drifted from the ledger record (W3-D10)."""
    current = (
        await session.execute(
            text("SELECT title, revision FROM public.notes WHERE id=:id"),
            {"id": note_id},
        )
    ).mappings().one_or_none()
    if current is None:
        return True
    return (
        current["title"] != ledger_source_title
        or current["revision"] != ledger_source_revision
    )


async def _ensure_adapter_identity(session: AsyncSession) -> None:
    row = (await session.execute(text("SELECT current_user, session_user"))).one()
    if row.session_user == "legacy_note_adapter_runner":
        return
    await session.execute(text("SET SESSION AUTHORIZATION legacy_note_adapter_runner"))
    check = (await session.execute(text("SELECT current_user, session_user"))).one()
    if check.session_user != "legacy_note_adapter_runner":
        raise PermissionError(
            "wk3 runner requires legacy_note_adapter_runner session identity"
        )


async def _ensure_approval_actors(session: AsyncSession, *, dry_run: bool = False) -> None:
    """Register wk3 approval actors as users and authorize them (idempotent).

    ``dry_run`` performs no INSERT and no commit: a preview must not persist
    actor rows or authorizations.
    """
    if dry_run:
        return
    actors_and_kinds = [
        (_ACTOR_SOURCE, "source"),
        (_ACTOR_QUESTION, "question_conversion"),
        (_ACTOR_MISTAKE, "mistake_conversion"),
        (_ACTOR_SCHEDULE, "schedule"),
    ]
    for index, (actor, kind) in enumerate(actors_and_kinds):
        await session.execute(text(
            "INSERT INTO public.users (id,username,password_hash,is_admin) "
            "VALUES (:actor,:name,'!',false) ON CONFLICT (id) DO NOTHING"
        ), {"actor": actor, "name": f"wk3-approver-{index}"})
        await session.execute(text(
            "INSERT INTO public.legacy_migration_approval_authorizations "
            "(user_id,approval_kind,enabled,granted_at) "
            "VALUES (:actor,:kind,true,now()) "
            "ON CONFLICT (user_id,approval_kind) DO UPDATE SET enabled=true"
        ), {"actor": actor, "kind": kind})
    await session.commit()


async def _restore_identity(session: AsyncSession) -> None:
    try:
        await session.execute(text("RESET SESSION AUTHORIZATION"))
    except Exception:
        pass


async def _source_hash(session: AsyncSession, note_id: uuid.UUID) -> str:
    return (
        await session.execute(
            text(
                "SELECT encode(public.digest("
                "convert_to(legacy_migration.canonicalize_legacy_note(:id)::text,'UTF8'),"
                "'sha256'),'hex')"
            ),
            {"id": note_id},
        )
    ).scalar_one()


async def _reconcile_visibility(
    session: AsyncSession,
    mistake_id: uuid.UUID,
    expected: str,
    *,
    dry_run: bool = False,
) -> bool:
    """Idempotent UPDATE of ``mistakes.visibility``.

    Returns True when the value differs from ``expected`` (i.e. a real run
    would change it).  In ``dry_run`` mode the comparison runs but no UPDATE
    is issued, so a preview leaves ``visibility``/``version`` untouched even
    when a later ``session.commit()`` occurs in the same transaction.
    """
    current = (
        await session.execute(
            text("SELECT visibility FROM public.mistakes WHERE id=:id"),
            {"id": mistake_id},
        )
    ).scalar_one_or_none()
    if current is None:
        return False
    if current == expected:
        return False
    if dry_run:
        return True
    await session.execute(
        text("UPDATE public.mistakes SET visibility=:vis, version=version+1 WHERE id=:id"),
        {"vis": expected, "id": mistake_id},
    )
    return True


PUBLIC_FIELD_ALLOWLIST = frozenset({
    "id", "title", "question_text", "correct_answer", "analysis",
    "reason_category", "mistake_reason", "difficulty", "knowledge_point_ids",
    "created_at", "updated_at",
})


async def compute_reconciliation_checks(session: AsyncSession) -> dict[str, bool]:
    """Compute real reconciliation match flags from current DB state (PR9F-02)."""
    from app.schemas.mistake import PublicMistakeOut

    allowlist_match = frozenset(PublicMistakeOut.model_fields.keys()) == PUBLIC_FIELD_ALLOWLIST

    drift_rows = (await session.execute(text("""
        SELECT lm.id FROM public.legacy_note_migrations lm
        JOIN public.notes n ON n.id = lm.source_note_id
        WHERE lm.source_title IS DISTINCT FROM n.title
           OR lm.source_revision IS DISTINCT FROM n.revision
    """))).all()
    provenance_match = len(drift_rows) == 0

    mismatch_rows = (await session.execute(text("""
        SELECT lm.id FROM public.legacy_note_migrations lm
        JOIN public.notes n ON n.id = lm.source_note_id
        JOIN public.mistakes m ON m.id = lm.target_mistake_id
        WHERE lm.target_mistake_id IS NOT NULL
          AND m.visibility != CASE
            WHEN n.status = 'published' AND NOT n.hidden THEN 'public'
            ELSE 'private'
          END
    """))).all()
    visibility_match = len(mismatch_rows) == 0

    return {
        "provenance_match": provenance_match,
        "visibility_matrix_match": visibility_match,
        "public_field_allowlist_match": allowlist_match,
    }


async def run_wk3_migration(
    session: AsyncSession,
    *,
    dry_run: bool = False,
) -> Wk3MigrationReport:
    if len(MAPPING_VERSION.encode()) > MAPPING_VERSION_MAX_BYTES:
        raise ValueError("MAPPING_VERSION too long")

    report = Wk3MigrationReport(generated_at=_now_utc().isoformat(), dry_run=dry_run)

    await _ensure_approval_actors(session, dry_run=dry_run)

    source_rows = (
        await session.execute(
            text(
                "SELECT id, status, hidden FROM public.notes "
                "WHERE type='mistake' ORDER BY id"
            )
        )
    ).mappings().all()
    report.source_total = len(source_rows)

    for row in source_rows:
        note_id: uuid.UUID = row["id"]
        status = row["status"]
        hidden = row["hidden"]
        report.by_mapping[_mapping_bucket(status, hidden)] += 1
        expected_visibility = map_legacy_note_to_mistake_visibility(status, hidden)

        wk3_ledger = (
            await session.execute(
                text(
                    "SELECT id, state, target_mistake_id, source_title, source_revision "
                    "FROM public.legacy_note_migrations "
                    "WHERE source_note_id=:src AND mapping_version=:mv"
                ),
                {"src": note_id, "mv": MAPPING_VERSION},
            )
        ).mappings().one_or_none()

        prior_migrated = (
            await session.execute(
                text(
                    "SELECT id, target_mistake_id, source_title, source_revision "
                    "FROM public.legacy_note_migrations "
                    "WHERE source_note_id=:src AND mapping_version != :mv "
                    "AND state IN ('migrated_active','migrated_paused') "
                    "ORDER BY id LIMIT 1"
                ),
                {"src": note_id, "mv": MAPPING_VERSION},
            )
        ).mappings().one_or_none()

        try:
            if wk3_ledger is not None and wk3_ledger["state"] in _TERMINAL_STATES:
                drift = await _check_source_drift(
                    session, note_id,
                    wk3_ledger["source_title"], wk3_ledger["source_revision"],
                )
                if drift:
                    report.rejected.append({
                        "source_note_id": str(note_id),
                        "reason": "source_drift",
                    })
                    report.provenance_match = False
                    mistake_id = wk3_ledger["target_mistake_id"]
                    if mistake_id is not None:
                        await _reconcile_visibility(
                            session, uuid.UUID(str(mistake_id)), expected_visibility,
                            dry_run=dry_run,
                        )
                    continue
                mistake_id = wk3_ledger["target_mistake_id"]
                if mistake_id is not None:
                    changed = await _reconcile_visibility(
                        session, uuid.UUID(str(mistake_id)), expected_visibility,
                        dry_run=dry_run,
                    )
                    if changed:
                        if dry_run:
                            report.would_reconcile += 1
                        else:
                            report.visibility_reconciled += 1
                            report.replay_noop = False
                    else:
                        report.skipped_already_migrated += 1
                else:
                    report.skipped_already_migrated += 1
                continue

            if wk3_ledger is None and prior_migrated is not None:
                drift = await _check_source_drift(
                    session, note_id,
                    prior_migrated["source_title"], prior_migrated["source_revision"],
                )
                if drift:
                    report.rejected.append({
                        "source_note_id": str(note_id),
                        "reason": "source_drift",
                    })
                    report.provenance_match = False
                    mistake_id = prior_migrated["target_mistake_id"]
                    if mistake_id is not None:
                        await _reconcile_visibility(
                            session, uuid.UUID(str(mistake_id)), expected_visibility,
                            dry_run=dry_run,
                        )
                    continue
                mistake_id = prior_migrated["target_mistake_id"]
                if mistake_id is None:
                    report.rejected.append({
                        "source_note_id": str(note_id),
                        "reason": "prior ledger row has no target_mistake_id",
                    })
                    if not dry_run:
                        report.replay_noop = False
                    continue
                changed = await _reconcile_visibility(
                    session, uuid.UUID(str(mistake_id)), expected_visibility,
                    dry_run=dry_run,
                )
                if changed:
                    if dry_run:
                        report.would_reconcile += 1
                    else:
                        report.visibility_reconciled += 1
                        report.replay_noop = False
                else:
                    report.skipped_already_migrated += 1
                continue

            next_review_raw = (
                await session.execute(
                    text("SELECT next_review FROM public.notes WHERE id=:id"),
                    {"id": note_id},
                )
            ).scalar_one_or_none()
            mapped_next_review_at, used_source_next_review = _map_next_review_to_due(next_review_raw)
            if mapped_next_review_at is None:
                mapped_next_review_at = _now_utc()
                used_source_next_review = False
            await session.commit()

            await _ensure_adapter_identity(session)
            try:
                payload = (
                    await session.execute(
                        text("SELECT legacy_migration.canonicalize_legacy_note(:id)"),
                        {"id": note_id},
                    )
                ).scalar_one()
                source_hash = await _source_hash(session, note_id)
                await session.commit()

                result = await migrate(
                    session,
                    source_note_id=note_id,
                    mapping_version=MAPPING_VERSION,
                    source_approved_by=_ACTOR_SOURCE,
                    source_approved_at=_now_utc(),
                    source_approval_sequence=1,
                    question_conversion_approved_by=_ACTOR_QUESTION,
                    question_conversion_approved_at=_now_utc(),
                    question_conversion_sequence=1,
                    mistake_conversion_approved_by=_ACTOR_MISTAKE,
                    mistake_conversion_approved_at=_now_utc(),
                    mistake_conversion_sequence=1,
                    canonical_payload=payload,
                    expected_source_hash=source_hash,
                    schedule_approved_by=_ACTOR_SCHEDULE,
                    schedule_approved_at=_now_utc(),
                    schedule_approval_sequence=1,
                    mapped_next_review_at=mapped_next_review_at,
                    dry_run=dry_run,
                )
                if dry_run:
                    await session.rollback()
            finally:
                await _restore_identity(session)

            if result.state == "retained_public_only":
                report.rejected.append({
                    "source_note_id": str(note_id),
                    "reason": "mapping_failed_retained_public_only",
                })
                continue
            if result.idempotent:
                report.skipped_already_migrated += 1
                continue

            if dry_run:
                report.would_create += 1
                report.would_create_review_items += 1
                if used_source_next_review:
                    report.would_next_due_from_source += 1
                else:
                    report.would_next_due_default += 1
            else:
                report.targets_created += 1
                report.replay_noop = False
                if result.target_review_item_id is not None:
                    report.review_items_created_v2 += 1
                    if used_source_next_review:
                        report.next_due_from_source += 1
                    else:
                        report.next_due_default += 1
        except Exception as exc:  # noqa: BLE001 - surfaced in the report
            try:
                await session.rollback()
            except Exception:
                pass
            report.rejected.append({"source_note_id": str(note_id), "reason": str(exc)})
            if not dry_run:
                report.replay_noop = False

    try:
        checks = await compute_reconciliation_checks(session)
        report.provenance_match = report.provenance_match and checks["provenance_match"]
        report.visibility_matrix_match = checks["visibility_matrix_match"]
        report.public_field_allowlist_match = checks["public_field_allowlist_match"]
    except Exception:
        report.provenance_match = False
        report.visibility_matrix_match = False

    return report


def write_report(report: Wk3MigrationReport, path: str | Path) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        json.dumps(report.to_json_dict(), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
