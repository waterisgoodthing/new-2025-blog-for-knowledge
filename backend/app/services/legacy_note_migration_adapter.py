"""The only application entry point for the isolated legacy-note rehearsal.

The adapter deliberately accepts an already canonicalized payload and an
expected hash.  It executes on the dedicated runner role, creates the target
chain in one transaction, and delegates ledger state/approval mutation to the
owner functions installed by revision 026.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, date, timedelta, timezone
import hashlib
import json
import uuid

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


@dataclass(frozen=True)
class LegacyNoteMigrationResult:
    ledger_id: uuid.UUID
    source_note_id: uuid.UUID
    source_hash: str
    state: str
    target_question_draft_item_id: uuid.UUID | None = None
    target_question_draft_id: uuid.UUID | None = None
    target_question_id: uuid.UUID | None = None
    target_question_source_id: uuid.UUID | None = None
    target_mistake_draft_item_id: uuid.UUID | None = None
    target_mistake_draft_id: uuid.UUID | None = None
    target_mistake_id: uuid.UUID | None = None
    target_review_item_id: uuid.UUID | None = None
    target_qkp_ids: tuple[int, ...] | None = None
    target_projection_ids: tuple[int, ...] | None = None
    target_bundle_hash: str | None = None
    manual_review_required: bool = True
    idempotent: bool = False


def _uuid(value: object | None) -> uuid.UUID | None:
    return None if value is None else uuid.UUID(str(value))


def _hash_payload(payload: dict) -> str:
    encoded = json.dumps(payload, ensure_ascii=False, separators=(",", ":"), sort_keys=True).encode()
    return hashlib.sha256(encoded).hexdigest()


def build_legacy_migration_idempotency_key(
    source_note_id: uuid.UUID | str,
    mapping_version: str,
    source_revision: int,
    source_hash: str,
) -> str:
    """Build the bounded key from the complete immutable source identity."""
    source_uuid = uuid.UUID(str(source_note_id))
    if not isinstance(mapping_version, str) or not mapping_version or len(mapping_version.encode()) > 64:
        raise ValueError("INVALID_IDEMPOTENCY_IDENTITY")
    if isinstance(source_revision, bool) or not isinstance(source_revision, int) or source_revision <= 0:
        raise ValueError("INVALID_IDEMPOTENCY_IDENTITY")
    if not isinstance(source_hash, str) or len(source_hash) != 64 or source_hash != source_hash.lower() or any(
        character not in "0123456789abcdef" for character in source_hash
    ):
        raise ValueError("INVALID_IDEMPOTENCY_IDENTITY")
    identity = f"legacy-note-migration|{source_uuid}|{source_revision}|{source_hash}|{mapping_version}".encode()
    return f"legacy:{hashlib.sha256(identity).hexdigest()}"


_UUID_NAMESPACE = uuid.uuid5(uuid.NAMESPACE_URL, "legacy-note-migration")


def _stable_id(source_note_id: uuid.UUID, mapping_version: str, kind: str) -> uuid.UUID:
    return uuid.uuid5(_UUID_NAMESPACE, f"{source_note_id}:{mapping_version}:{kind}")


def _as_datetime(value: object | None) -> datetime | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value
    if isinstance(value, date):
        raise ValueError("DATE_AMBIGUOUS")
    raw = str(value).replace("Z", "+00:00")
    if "T" not in raw:
        raise ValueError("DATE_AMBIGUOUS")
    return datetime.fromisoformat(raw)


def _validate_utc_instant(value: object | None) -> datetime:
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() != timedelta(0):
        raise ValueError("DATE_AMBIGUOUS")
    return value.astimezone(timezone.utc)


def _validate_schedule(
    *,
    mapped_next_review_at: datetime | None,
    schedule_approved_by: uuid.UUID | None,
    schedule_approved_at: datetime | None,
    schedule_approval_sequence: int | None,
) -> datetime | None:
    """Validate the complete active schedule without inventing a timestamp."""
    schedule_values = (schedule_approved_by, schedule_approved_at, schedule_approval_sequence)
    has_schedule = any(value is not None for value in schedule_values)
    complete_schedule = all(value is not None for value in schedule_values)
    if not has_schedule and mapped_next_review_at is None:
        return None
    if not complete_schedule:
        raise ValueError("APPROVAL_REQUIRED")
    if not isinstance(schedule_approval_sequence, int) or isinstance(schedule_approval_sequence, bool) or schedule_approval_sequence <= 0:
        raise ValueError("INVALID_REASON_OR_REQUIRED_PARAMETER")
    if not isinstance(schedule_approved_at, datetime) or schedule_approved_at.tzinfo is None or schedule_approved_at.utcoffset() != timedelta(0):
        raise ValueError("INVALID_REASON_OR_REQUIRED_PARAMETER")
    if mapped_next_review_at is None:
        raise ValueError("DATE_AMBIGUOUS")
    return _validate_utc_instant(mapped_next_review_at)


def validate_legacy_mapping_payload(payload: dict) -> dict:
    """Validate the frozen mapping inputs without inventing source values."""
    subject_id = payload.get("subject_id")
    if isinstance(subject_id, bool) or not isinstance(subject_id, int) or subject_id <= 0:
        raise ValueError("SUBJECT_UNMAPPED")
    question = payload.get("question")
    if not isinstance(question, str) or not question.strip():
        raise ValueError("QUESTION_INVALID")
    question_type = payload.get("question_type")
    if question_type == "essay":
        raise ValueError("ESSAY_MANUAL_REQUIRED")
    if question_type not in {"true_false", "single_choice", "multiple_choice", "short_answer"}:
        raise ValueError("QUESTION_INVALID")
    answers = payload.get("answers")
    if not isinstance(answers, dict):
        raise ValueError("ANSWER_INVALID")
    correct_answer = answers.get("correct_answer")
    if not isinstance(correct_answer, str) or not correct_answer.strip():
        raise ValueError("ANSWER_INVALID")
    options = payload.get("options")
    if isinstance(options, list) and options and all(isinstance(item, str) for item in options):
        options = [{"key": chr(65 + index), "text": item} for index, item in enumerate(options)]
    if not isinstance(options, list):
        raise ValueError("QUESTION_INVALID")
    if question_type in {"short_answer", "true_false"} and options:
        raise ValueError("QUESTION_INVALID")
    if question_type in {"single_choice", "multiple_choice"} and len(options) < 2:
        raise ValueError("QUESTION_INVALID")
    option_keys: set[str] = set()
    for item in options:
        if (
            not isinstance(item, dict)
            or set(item) != {"key", "text"}
            or not isinstance(item["key"], str)
            or not isinstance(item["text"], str)
            or not item["key"].strip()
            or not item["text"].strip()
        ):
            raise ValueError("QUESTION_INVALID")
        if item["key"] in option_keys:
            raise ValueError("QUESTION_INVALID")
        option_keys.add(item["key"])
    if question_type == "true_false" and correct_answer not in {"True", "False"}:
        raise ValueError("ANSWER_INVALID")
    if question_type in {"single_choice", "multiple_choice"}:
        answer_parts = [part.strip() for part in correct_answer.split(",")]
        if any(not part for part in answer_parts):
            raise ValueError("ANSWER_INVALID")
        if question_type == "single_choice" and (
            len(answer_parts) != 1 or answer_parts[0] not in option_keys
        ):
            raise ValueError("ANSWER_INVALID")
        if question_type == "multiple_choice" and (
            not answer_parts or len(set(answer_parts)) != len(answer_parts)
            or any(part not in option_keys for part in answer_parts)
        ):
            raise ValueError("ANSWER_INVALID")
    for name in ("interval", "repetitions"):
        value = payload.get(name)
        if isinstance(value, bool) or not isinstance(value, int) or value < 0:
            raise ValueError("CANONICAL_PAYLOAD_INVALID")
    knowledge_points = payload.get("knowledge_points")
    if not isinstance(knowledge_points, list) or not knowledge_points:
        raise ValueError("KP_UNMAPPED_OR_AMBIGUOUS")
    return {
        "subject_id": subject_id,
        "question": question,
        "question_type": question_type,
        "answers": answers,
        "options": options,
        "answer_data": {
            "kind": question_type,
            "value": (
                correct_answer == "True"
                if question_type == "true_false"
                else [part.strip() for part in correct_answer.split(",")]
                if question_type in {"single_choice", "multiple_choice"}
                else correct_answer
            ),
        },
        "knowledge_points": knowledge_points,
    }


def build_question_source_provenance(
    *,
    source_note_id: uuid.UUID | str,
    mapping_version: str,
    source_hash: str,
    payload: dict,
    normalized: dict,
) -> dict:
    """Build the frozen QuestionSource JSON metadata without copying source prose."""
    source_uuid = uuid.UUID(str(source_note_id))
    if not isinstance(mapping_version, str) or not mapping_version or len(mapping_version.encode()) > 64:
        raise ValueError("SOURCE_PROVENANCE_INVALID")
    if not isinstance(source_hash, str) or len(source_hash) != 64 or source_hash != source_hash.lower() or any(
        character not in "0123456789abcdef" for character in source_hash
    ):
        raise ValueError("SOURCE_PROVENANCE_INVALID")
    required_text = ("slug", "title", "source_url")
    if any(not isinstance(payload.get(name), str) or not payload[name] for name in required_text):
        raise ValueError("SOURCE_PROVENANCE_INVALID")
    revision = payload.get("revision")
    if isinstance(revision, bool) or not isinstance(revision, int) or revision <= 0:
        raise ValueError("SOURCE_PROVENANCE_INVALID")
    difficulty = payload.get("difficulty") if payload.get("difficulty") in {"easy", "medium", "hard"} else None
    mirror_contract = {
        "subject_id": normalized["subject_id"],
        "title": payload["title"],
        "question_text": normalized["question"],
        "stem_md": payload.get("content") or "",
        "question_type": normalized["question_type"],
        "options": normalized["options"],
        "difficulty": difficulty,
        "correct_answer": normalized["answers"]["correct_answer"],
        "answer_data": normalized["answer_data"],
        "analysis_md": payload.get("analysis"),
        "explanation": payload.get("analysis"),
    }
    return {
        "source_note_id": str(source_uuid),
        "source_slug": payload["slug"],
        "source_title": payload["title"],
        "source_url": payload["source_url"],
        "source_hash": source_hash,
        "mapping_version": mapping_version,
        "source_revision": revision,
        "mirror_contract": mirror_contract,
    }


def build_legacy_migration_notes(payload: dict) -> list[dict]:
    """Keep explicit notes or emit only the frozen field-matrix lossiness codes."""
    explicit = payload.get("migration_notes")
    if explicit is not None:
        if not isinstance(explicit, list) or any(not isinstance(note, dict) for note in explicit):
            raise ValueError("MIGRATION_NOTES_INVALID")
        return explicit
    notes: list[dict] = []
    if payload.get("content") is not None:
        notes.append({
            "code": "CONTENT_PROVENANCE_ONLY",
            "field": "content",
            "lossiness": "formal_target_not_mapped",
        })
    if payload.get("legacy_review_json") is not None:
        notes.append({
            "code": "LEGACY_REVIEW_PROVENANCE_ONLY",
            "field": "legacy_review_json",
            "lossiness": "review_history_not_recreated",
        })
    if isinstance(payload.get("knowledge_points"), list):
        notes.append({
            "code": "MISTAKE_PROJECTION_ID_SET_ONLY",
            "field": "knowledge_points",
            "lossiness": "projection_role_order_not_represented",
        })
    return notes


def should_retain_public_only(payload: dict) -> bool:
    """Return true only for public sources rejected by the deterministic mapper."""
    if payload.get("status") != "published" or payload.get("hidden") is not False:
        return False
    try:
        validate_legacy_mapping_payload(payload)
    except ValueError as exc:
        return str(exc) in {
            "SUBJECT_UNMAPPED",
            "QUESTION_INVALID",
            "ANSWER_INVALID",
            "KP_UNMAPPED_OR_AMBIGUOUS",
        }
    return False


async def _assert_runner(session: AsyncSession) -> None:
    row = (await session.execute(text("SELECT current_user, session_user"))).one()
    if row.current_user != "legacy_note_adapter_runner" or row.session_user != "legacy_note_adapter_runner":
        raise PermissionError("legacy migration adapter requires legacy_note_adapter_runner")


async def _ledger(session: AsyncSession, ledger_id: uuid.UUID, *, idempotent: bool) -> LegacyNoteMigrationResult:
    row = (await session.execute(text("""
        SELECT id,source_note_id,source_hash,state,
          target_question_draft_item_id,target_question_draft_id,target_question_id,
          target_question_source_id,target_mistake_draft_item_id,target_mistake_draft_id,
          target_mistake_id,target_review_item_id,target_qkp_ids,target_projection_ids,
          target_bundle_hash,manual_review_required
        FROM public.legacy_note_migrations WHERE id=:id
    """), {"id": ledger_id})).mappings().one()
    return LegacyNoteMigrationResult(
        ledger_id=row["id"], source_note_id=row["source_note_id"], source_hash=str(row["source_hash"]),
        state=row["state"], target_question_draft_item_id=row["target_question_draft_item_id"],
        target_question_draft_id=row["target_question_draft_id"], target_question_id=row["target_question_id"],
        target_question_source_id=row["target_question_source_id"],
        target_mistake_draft_item_id=row["target_mistake_draft_item_id"],
        target_mistake_draft_id=row["target_mistake_draft_id"], target_mistake_id=row["target_mistake_id"],
        target_review_item_id=row["target_review_item_id"],
        target_qkp_ids=None if row["target_qkp_ids"] is None else tuple(row["target_qkp_ids"]),
        target_projection_ids=None if row["target_projection_ids"] is None else tuple(row["target_projection_ids"]),
        target_bundle_hash=row["target_bundle_hash"], manual_review_required=row["manual_review_required"],
        idempotent=idempotent,
    )


async def _create_targets(
    session: AsyncSession,
    *,
    source_note_id: uuid.UUID,
    source_hash: str,
    mapping_version: str,
    payload: dict,
    question_actor_id: uuid.UUID,
    mistake_actor_id: uuid.UUID,
    active: bool,
    next_review_at: datetime | None,
    include_mistake: bool = False,
) -> dict[str, object]:
    normalized = validate_legacy_mapping_payload(payload)
    source_provenance = build_question_source_provenance(
        source_note_id=source_note_id,
        mapping_version=mapping_version,
        source_hash=source_hash,
        payload=payload,
        normalized=normalized,
    )
    subject_id = normalized["subject_id"]
    question_text = normalized["question"]
    correct_answer = normalized["answers"]["correct_answer"]
    qtype = normalized["question_type"]
    options = normalized["options"]
    kp_names = normalized["knowledge_points"]
    if any(not isinstance(name, str) or not name.strip() for name in kp_names):
        raise ValueError("KP_UNMAPPED_OR_AMBIGUOUS")
    kp_rows = (await session.execute(text("""
      SELECT id,name FROM public.knowledge_points
       WHERE subject_id=:subject AND lower(name) = ANY(:names)
       ORDER BY id
    """), {"subject": subject_id, "names": [str(name).strip().lower() for name in kp_names]})).mappings().all()
    if len(kp_rows) != len(set(str(name).strip().lower() for name in kp_names)):
        raise ValueError("KP_UNMAPPED_OR_AMBIGUOUS")
    kp_ids = [int(row["id"]) for row in kp_rows]
    question_id = _stable_id(source_note_id, mapping_version, "question")
    question_draft_item_id = _stable_id(source_note_id, mapping_version, "question-draft-item")
    question_draft_id = _stable_id(source_note_id, mapping_version, "question-draft")
    question_source_id = _stable_id(source_note_id, mapping_version, "question-source")
    mistake_draft_item_id = _stable_id(source_note_id, mapping_version, "mistake-draft-item")
    mistake_draft_id = _stable_id(source_note_id, mapping_version, "mistake-draft")
    mistake_id = _stable_id(source_note_id, mapping_version, "mistake")
    review_item_id = _stable_id(source_note_id, mapping_version, "review-item") if active else None
    title = payload.get("title")
    difficulty = payload.get("difficulty") if payload.get("difficulty") in {"easy", "medium", "hard"} else None
    interval = payload["interval"]
    repetitions = payload["repetitions"]
    if active:
        next_review_at = _validate_utc_instant(next_review_at)
    elif next_review_at is not None:
        raise ValueError("INVALID_REASON_OR_REQUIRED_PARAMETER")

    await session.execute(text("""
      INSERT INTO public.draft_items
        (id,draft_type,source_type,source_id,status,version,target_type,target_id,created_by,
         source_hash,approved_by,approved_at,conversion_sequence,target_question_id)
      VALUES (:id,'question','legacy_note',:source_id,'converted',1,'question',CAST(:target AS text),:actor,
         :source_hash,:actor,now(),1,CAST(:target AS uuid))
    """), {"id": question_draft_item_id, "source_id": str(source_note_id), "target": str(question_id),
            "actor": question_actor_id, "source_hash": source_hash})
    await session.execute(text("""
      INSERT INTO public.question_drafts
        (id,draft_item_id,subject_id,title,question_text,question_type,options,correct_answer,explanation,difficulty)
      VALUES (:id,:draft,:subject,:title,:question,:type,CAST(:options AS json),:answer,:explanation,:difficulty)
    """), {"id": question_draft_id, "draft": question_draft_item_id, "subject": subject_id,
            "title": title, "question": question_text, "type": qtype, "options": json.dumps(options),
            "answer": correct_answer, "explanation": payload.get("analysis"), "difficulty": difficulty})
    await session.execute(text("""
      INSERT INTO public.questions
        (id,subject_id,title,stem_md,question_text,question_type,options,answer_data,correct_answer,
         analysis_md,explanation,difficulty,status,visibility,version)
      VALUES (:id,:subject,:title,:stem,:question,:type,CAST(:options AS json),CAST(:answer_data AS json),
         :answer,:analysis,:explanation,:difficulty,'active','private',1)
    """), {"id": question_id, "subject": subject_id, "title": title, "stem": payload.get("content") or "",
            "question": question_text, "type": qtype, "options": json.dumps(options),
            "answer_data": json.dumps(normalized["answer_data"]), "answer": correct_answer,
            "analysis": payload.get("analysis"), "explanation": payload.get("analysis"), "difficulty": difficulty})
    await session.execute(text("""
      INSERT INTO public.question_sources
        (id,question_id,source_type,source_title,source_ref,source_url,source_note)
      VALUES (:id,:question,'note',:title,:ref,:url,:note)
    """), {"id": question_source_id, "question": question_id, "title": title,
            "ref": f"legacy-note:{source_note_id}", "url": payload.get("source_url"),
        "note": json.dumps(source_provenance, ensure_ascii=False, separators=(",", ":"))})
    for order, kp_id in enumerate(kp_ids):
        await session.execute(text("""
          INSERT INTO public.question_knowledge_points(question_id,knowledge_point_id,role,sort_order)
          VALUES (:question,:kp,'primary',:sort)
        """), {"question": question_id, "kp": kp_id, "sort": order})

    if not include_mistake:
        return {
            "target_question_draft_item_id": question_draft_item_id,
            "target_question_draft_id": question_draft_id,
            "target_question_id": question_id,
            "target_question_source_id": question_source_id,
            "target_mistake_draft_item_id": mistake_draft_item_id,
            "target_mistake_draft_id": mistake_draft_id,
            "target_mistake_id": mistake_id,
            "target_review_item_id": review_item_id,
            "target_qkp_ids": kp_ids,
            "target_projection_ids": [],
        }

    mistake_reason = "legacy_note_migration"
    await session.execute(text("""
      INSERT INTO public.draft_items
        (id,draft_type,source_type,source_id,status,version,target_type,target_id,created_by,
         source_hash,approved_by,approved_at,conversion_sequence,target_mistake_id)
      VALUES (:id,'mistake','question',:source_id,'converted',1,'mistake',CAST(:target AS text),:actor,
         :source_hash,:actor,now(),1,CAST(:target AS uuid))
    """), {"id": mistake_draft_item_id, "source_id": str(question_id), "target": str(mistake_id),
            "actor": mistake_actor_id, "source_hash": source_hash})
    await session.execute(text("""
      INSERT INTO public.mistake_drafts
        (id,draft_item_id,question_id,subject_id,title,question_text,my_answer,correct_answer_snapshot,
         explanation_snapshot,reason_category,mistake_reason,difficulty)
      VALUES (:id,:draft,CAST(:question AS uuid),:subject,:title,:question_text,:my_answer,:correct,:explanation,
         'unknown',:reason,:difficulty)
    """), {"id": mistake_draft_id, "draft": mistake_draft_item_id, "question": question_id,
            "subject": subject_id, "title": title, "question_text": question_text, "my_answer": (payload.get("answers") or {}).get("my_answer"),
            "correct": correct_answer, "explanation": payload.get("analysis"), "reason": mistake_reason,
            "difficulty": difficulty})
    await session.execute(text("""
      INSERT INTO public.mistakes
        (id,source_draft_item_id,question_id,subject_id,title,question_text,my_answer,correct_answer,
         analysis,reason_category,mistake_reason,difficulty,status,visibility,version)
      VALUES (:id,:draft,CAST(:question AS uuid),:subject,:title,:question_text,:my_answer,:correct,:analysis,
         'unknown',:reason,:difficulty,'active','private',1)
    """), {"id": mistake_id, "draft": mistake_draft_item_id, "question": question_id,
            "subject": subject_id, "title": title, "question_text": question_text, "my_answer": (payload.get("answers") or {}).get("my_answer"),
            "correct": correct_answer, "analysis": payload.get("analysis"), "reason": mistake_reason,
            "difficulty": difficulty})
    if review_item_id:
        await session.execute(text("""
          INSERT INTO public.review_items
            (id,target_type,target_id,state,algorithm,interval_days,repetitions,next_review_at,last_reviewed_at,mistake_id)
          VALUES (:id,'mistake',:target,'active','fixed_interval_v1',:interval,:repetitions,:next_review,:last,:mistake)
        """), {"id": review_item_id, "target": str(mistake_id), "interval": interval,
                "repetitions": repetitions, "next_review": next_review_at,
                "last": _as_datetime(payload.get("last_reviewed")), "mistake": mistake_id})
    projection_ids: list[int] = []
    for kp_id in kp_ids:
        projection = (await session.execute(text("""
          INSERT INTO public.knowledge_point_links(knowledge_point_id,target_type,target_id)
          VALUES (:kp,'mistake',:target) RETURNING id
        """), {"kp": kp_id, "target": str(mistake_id)})).scalar_one()
        projection_ids.append(int(projection))
    return {
        "target_question_draft_item_id": question_draft_item_id, "target_question_draft_id": question_draft_id,
        "target_question_id": question_id, "target_question_source_id": question_source_id,
        "target_mistake_draft_item_id": mistake_draft_item_id, "target_mistake_draft_id": mistake_draft_id,
        "target_mistake_id": mistake_id, "target_review_item_id": review_item_id,
        "target_qkp_ids": kp_ids, "target_projection_ids": projection_ids,
    }


async def _finish_mistake_targets(
    session: AsyncSession,
    *,
    question_id: uuid.UUID,
    mistake_draft_item_id: uuid.UUID,
    mistake_draft_id: uuid.UUID,
    mistake_id: uuid.UUID,
    review_item_id: uuid.UUID | None,
    subject_id: int,
    title: str | None,
    question_text: str,
    answers: dict,
    analysis: str | None,
    difficulty: str | None,
    source_hash: str,
    mistake_actor_id: uuid.UUID,
    kp_ids: list[int],
    interval: int,
    repetitions: int,
    last_reviewed: object | None,
    next_review_at: datetime | None,
) -> list[int]:
    """Create the mistake side only after its independent approval is recorded."""
    await session.execute(text("""
      INSERT INTO public.draft_items
        (id,draft_type,source_type,source_id,status,version,target_type,target_id,created_by,
         source_hash,approved_by,approved_at,conversion_sequence,target_mistake_id)
      VALUES (:id,'mistake','question',:source_id,'converted',1,'mistake',CAST(:target AS text),:actor,
         :source_hash,:actor,now(),1,CAST(:target AS uuid))
    """), {"id": mistake_draft_item_id, "source_id": str(question_id), "target": str(mistake_id),
            "actor": mistake_actor_id, "source_hash": source_hash})
    await session.execute(text("""
      INSERT INTO public.mistake_drafts
        (id,draft_item_id,question_id,subject_id,title,question_text,my_answer,correct_answer_snapshot,
         explanation_snapshot,reason_category,mistake_reason,difficulty)
      VALUES (:id,:draft,CAST(:question AS uuid),:subject,:title,:question_text,:my_answer,:correct,:explanation,
         'unknown','legacy_note_migration',:difficulty)
    """), {"id": mistake_draft_id, "draft": mistake_draft_item_id, "question": question_id,
            "subject": subject_id, "title": title, "question_text": question_text,
            "my_answer": answers.get("my_answer"), "correct": answers["correct_answer"],
            "explanation": analysis, "difficulty": difficulty})
    await session.execute(text("""
      INSERT INTO public.mistakes
        (id,source_draft_item_id,question_id,subject_id,title,question_text,my_answer,correct_answer,
         analysis,reason_category,mistake_reason,difficulty,status,visibility,version)
      VALUES (:id,:draft,CAST(:question AS uuid),:subject,:title,:question_text,:my_answer,:correct,:analysis,
         'unknown','legacy_note_migration',:difficulty,'active','private',1)
    """), {"id": mistake_id, "draft": mistake_draft_item_id, "question": question_id,
            "subject": subject_id, "title": title, "question_text": question_text,
            "my_answer": answers.get("my_answer"), "correct": answers["correct_answer"],
            "analysis": analysis, "difficulty": difficulty})
    if review_item_id:
        await session.execute(text("""
          INSERT INTO public.review_items
            (id,target_type,target_id,state,algorithm,interval_days,repetitions,next_review_at,last_reviewed_at,mistake_id)
          VALUES (:id,'mistake',:target,'active','fixed_interval_v1',:interval,:repetitions,:next_review,:last,:mistake)
        """), {"id": review_item_id, "target": str(mistake_id), "interval": interval,
                "repetitions": repetitions, "next_review": next_review_at,
                "last": _as_datetime(last_reviewed), "mistake": mistake_id})
    projection_ids: list[int] = []
    for kp_id in kp_ids:
        projection_ids.append(int((await session.execute(text("""
          INSERT INTO public.knowledge_point_links(knowledge_point_id,target_type,target_id)
          VALUES (:kp,'mistake',:target) RETURNING id
        """), {"kp": kp_id, "target": str(mistake_id)})).scalar_one()))
    return projection_ids


async def migrate(
    session: AsyncSession,
    *,
    source_note_id: uuid.UUID,
    mapping_version: str,
    source_approved_by: uuid.UUID,
    source_approved_at: datetime,
    source_approval_sequence: int,
    question_conversion_approved_by: uuid.UUID,
    question_conversion_approved_at: datetime,
    question_conversion_sequence: int,
    mistake_conversion_approved_by: uuid.UUID,
    mistake_conversion_approved_at: datetime,
    mistake_conversion_sequence: int,
    canonical_payload: dict,
    expected_source_hash: str,
    schedule_approved_by: uuid.UUID | None = None,
    schedule_approved_at: datetime | None = None,
    schedule_approval_sequence: int | None = None,
    mapped_next_review_at: datetime | None = None,
    dry_run: bool = False,
) -> LegacyNoteMigrationResult:
    """Migrate one canonical source note; callers must supply a runner session."""
    mapped_next_review_at = _validate_schedule(
        mapped_next_review_at=mapped_next_review_at,
        schedule_approved_by=schedule_approved_by,
        schedule_approved_at=schedule_approved_at,
        schedule_approval_sequence=schedule_approval_sequence,
    )
    await session.execute(text("SET TRANSACTION ISOLATION LEVEL SERIALIZABLE"))
    await _assert_runner(session)
    if len({source_approved_by, question_conversion_approved_by, mistake_conversion_approved_by}) != 3:
        raise ValueError("APPROVAL_ACTORS_MUST_BE_INDEPENDENT")
    if schedule_approved_by is not None and schedule_approved_by in {
        source_approved_by, question_conversion_approved_by, mistake_conversion_approved_by
    }:
        raise ValueError("APPROVAL_ACTORS_MUST_BE_INDEPENDENT")
    source_hash = expected_source_hash.lower()
    ledger_id = uuid.uuid4()
    payload_text = json.dumps(canonical_payload, ensure_ascii=False, separators=(",", ":"))
    live_payload = (await session.execute(text(
        "SELECT legacy_migration.canonicalize_legacy_note(:id)"), {"id": source_note_id}
    )).scalar_one()
    if canonical_payload != live_payload:
        raise ValueError("SOURCE_DRIFT")
    prior = (await session.execute(text("""
      SELECT id,state,source_hash,source_revision FROM public.legacy_note_migrations
      WHERE source_note_id=:source AND mapping_version=:mapping
    """), {"source": source_note_id, "mapping": mapping_version})).mappings().one_or_none()
    if prior is not None:
        ledger_id = prior["id"]
        if str(prior["source_hash"]) != source_hash or prior["source_revision"] != canonical_payload["revision"]:
            raise ValueError("existing migration source hash mismatch")
        if prior["state"] in {"migrated_active", "migrated_paused", "retained_public_only", "rolled_back"}:
            return await _ledger(session, ledger_id, idempotent=True)
    args = {
        "ledger": ledger_id, "source": source_note_id, "mapping": mapping_version,
        "hash": source_hash, "slug": canonical_payload["slug"], "title": canonical_payload["title"],
        "url": canonical_payload["source_url"], "status": canonical_payload["status"],
        "hidden": canonical_payload["hidden"], "revision": canonical_payload["revision"],
        "snapshot": f"sha256:{source_hash}", "idempotency": build_legacy_migration_idempotency_key(
            source_note_id, mapping_version, canonical_payload["revision"], source_hash
        ),
        "payload": payload_text, "review": json.dumps(canonical_payload["legacy_review_json"]),
        "notes": json.dumps(build_legacy_migration_notes(canonical_payload), ensure_ascii=False),
    }
    await session.execute(text("""
      SELECT legacy_migration.create_legacy_note_migration_pending(
        :ledger,:source,:mapping,:hash,:slug,:title,:url,:status,:hidden,:revision,:snapshot,:idempotency,
        CAST(:payload AS jsonb),CAST(:review AS jsonb),CAST(:notes AS jsonb))
    """), args)
    existing = (await session.execute(text(
        "SELECT id,state,target_question_id FROM public.legacy_note_migrations WHERE source_note_id=:source AND mapping_version=:mapping"
    ), {"source": source_note_id, "mapping": mapping_version})).one()
    ledger_id = existing.id
    if dry_run:
        return await _ledger(session, ledger_id, idempotent=False)
    if existing.state in {"migrated_active", "migrated_paused", "retained_public_only", "rolled_back"}:
        return await _ledger(session, ledger_id, idempotent=True)
    if should_retain_public_only(canonical_payload):
        await session.execute(text("""
          SELECT legacy_migration.record_legacy_note_migration_approval(
            :ledger,:mapping,:hash,'pending_mapping','source',:actor,:at,0,:sequence,'source approval','{}')
        """), {"ledger": ledger_id, "mapping": mapping_version, "hash": source_hash,
                "actor": source_approved_by, "at": source_approved_at, "sequence": source_approval_sequence})
        await session.execute(text("""
          SELECT legacy_migration.transition_legacy_note_migration(
            :ledger,'pending_mapping','retained_public_only',:actor,'retained',:source,:mapping,:hash,
            ROW(NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL::integer[],NULL::integer[])::legacy_migration.legacy_note_migration_target_bundle,
            NULL,NULL,NULL,NULL,'{}')
        """), {"ledger": ledger_id, "actor": source_approved_by, "source": source_note_id,
                "mapping": mapping_version, "hash": source_hash})
        return await _ledger(session, ledger_id, idempotent=False)
    bundle_args = {"ledger": ledger_id, "mapping": mapping_version, "hash": source_hash,
                   "source": source_note_id, "actor": source_approved_by, "at": source_approved_at,
                   "seq": source_approval_sequence}
    await session.execute(text("""
      SELECT legacy_migration.record_legacy_note_migration_approval(
        :ledger,:mapping,:hash,'pending_mapping','source',:actor,:at,0,:seq,'source approval','{}')
    """), bundle_args)
    await session.execute(text("""
      SELECT legacy_migration.transition_legacy_note_migration(
        :ledger,'pending_mapping','ready',:actor,'ready',:source,:mapping,:hash,
        ROW(NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,ARRAY[]::integer[],ARRAY[]::integer[])::legacy_migration.legacy_note_migration_target_bundle,
        NULL,NULL,NULL,NULL,'{}')
    """), bundle_args)
    targets = await _create_targets(
        session, source_note_id=source_note_id, source_hash=source_hash, mapping_version=mapping_version,
        payload=canonical_payload, question_actor_id=question_conversion_approved_by,
        mistake_actor_id=mistake_conversion_approved_by, active=mapped_next_review_at is not None,
        next_review_at=mapped_next_review_at,
        include_mistake=False,
    )
    bundle = {**targets}
    for kind, actor, approved_at, sequence in (
        ("question_conversion", question_conversion_approved_by, question_conversion_approved_at, question_conversion_sequence),
        ("mistake_conversion", mistake_conversion_approved_by, mistake_conversion_approved_at, mistake_conversion_sequence),
    ):
        await session.execute(text("""
          SELECT legacy_migration.record_legacy_note_migration_approval(
            :ledger,:mapping,:hash,'ready',:kind,:actor,:at,0,:seq,:reason,'{}')
        """), {"ledger": ledger_id, "mapping": mapping_version, "hash": source_hash,
                "kind": kind, "reason": kind, "actor": actor, "at": approved_at, "seq": sequence})
    active = mapped_next_review_at is not None
    if active:
        await session.execute(text("""
          SELECT legacy_migration.record_legacy_note_migration_approval(
            :ledger,:mapping,:hash,'ready','schedule',:actor,:at,0,:seq,'schedule','{}')
        """), {"ledger": ledger_id, "mapping": mapping_version, "hash": source_hash,
                "actor": schedule_approved_by, "at": schedule_approved_at, "seq": schedule_approval_sequence})
    normalized = validate_legacy_mapping_payload(canonical_payload)
    bundle["target_projection_ids"] = await _finish_mistake_targets(
        session, question_id=bundle["target_question_id"],
        mistake_draft_item_id=bundle["target_mistake_draft_item_id"],
        mistake_draft_id=bundle["target_mistake_draft_id"], mistake_id=bundle["target_mistake_id"],
        review_item_id=bundle["target_review_item_id"], subject_id=normalized["subject_id"],
        title=canonical_payload.get("title"), question_text=normalized["question"],
        answers=normalized["answers"], analysis=canonical_payload.get("analysis"),
        difficulty=canonical_payload.get("difficulty") if canonical_payload.get("difficulty") in {"easy", "medium", "hard"} else None,
        source_hash=source_hash, mistake_actor_id=mistake_conversion_approved_by,
        kp_ids=list(bundle["target_qkp_ids"]), interval=canonical_payload["interval"],
        repetitions=canonical_payload["repetitions"], last_reviewed=canonical_payload.get("last_reviewed"),
        next_review_at=mapped_next_review_at,
    )
    bundle_tuple = "ROW(:qditem,:qdraft,:question,:qsource,:mditem,:mdraft,:mistake,:review,CAST(:qkps AS integer[]),CAST(:projections AS integer[]))::legacy_migration.legacy_note_migration_target_bundle"
    transition = "migrated_active" if active else "migrated_paused"
    await session.execute(text(f"""
      SELECT legacy_migration.transition_legacy_note_migration(
        :ledger,'ready',:transition,:actor,:reason,:source,:mapping,:hash,{bundle_tuple},
        NULL,NULL,:next_review,NULL,'{{}}')
    """), {"ledger": ledger_id, "transition": transition, "actor": schedule_approved_by or mistake_conversion_approved_by,
            "reason": transition, "source": source_note_id, "mapping": mapping_version, "hash": source_hash,
            "qditem": bundle["target_question_draft_item_id"], "qdraft": bundle["target_question_draft_id"],
            "question": bundle["target_question_id"], "qsource": bundle["target_question_source_id"],
            "mditem": bundle["target_mistake_draft_item_id"], "mdraft": bundle["target_mistake_draft_id"],
            "mistake": bundle["target_mistake_id"], "review": bundle["target_review_item_id"],
            "qkps": list(bundle["target_qkp_ids"]), "projections": list(bundle["target_projection_ids"]),
            "next_review": mapped_next_review_at})
    return await _ledger(session, ledger_id, idempotent=False)
