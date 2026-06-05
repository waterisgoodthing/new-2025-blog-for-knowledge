from __future__ import annotations

from collections import defaultdict

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.note import Note, Tag
from app.schemas.knowledge import (
    NoteBrief,
    RelationSuggestion,
    RelationStatus,
    RelationType,
    SourceType,
)


def _split_knowledge_points(value: str | None) -> list[str]:
    if not value:
        return []
    normalized = value.replace("，", ",").replace("、", ",").replace("\n", ",").replace("；", ",")
    return [item.strip() for item in normalized.split(",") if item.strip()]


def _kp_overlap_score(a: list[str], b: list[str]) -> tuple[int, list[str]]:
    overlap = 0
    matched: list[str] = []
    for ka in a:
        for kb in b:
            if ka.lower() in kb.lower() or kb.lower() in ka.lower():
                overlap += 1
                matched.append(ka)
                break
    return overlap, matched


def _subject_match(a: str | None, b: str | None) -> bool:
    if not a or not b:
        return False
    return a.strip().lower() == b.strip().lower()


def _explain_relation(
    source: Note,
    target: Note,
    relation_type: RelationType,
    kp_matched: list[str],
    subject_matched: bool,
) -> str:
    parts: list[str] = []
    if subject_matched and source.subject:
        parts.append(f"同属「{source.subject}」")
    if kp_matched:
        parts.append(f"知识点重叠：{'、'.join(kp_matched[:3])}")
    if not parts:
        parts.append("内容相关")
    return "，".join(parts)


async def suggest_relations(
    db: AsyncSession,
    source_notes: list[NoteBrief],
    all_candidates: list[NoteBrief] | None = None,
    limit: int = 20,
) -> list[RelationSuggestion]:
    if not source_notes:
        return []

    source_ids = {n.id for n in source_notes}

    if all_candidates is None:
        candidate_ids = source_ids
        result = await db.execute(
            select(Note).options(selectinload(Note.tags)).where(Note.id.in_(candidate_ids))
        )
        all_db_notes = list(result.scalars().all())
    else:
        candidate_ids = {n.id for n in all_candidates} | source_ids
        result = await db.execute(
            select(Note).options(selectinload(Note.tags)).where(Note.id.in_(candidate_ids))
        )
        all_db_notes = list(result.scalars().all())

    note_map: dict[str, Note] = {str(n.id): n for n in all_db_notes}

    suggestions: list[RelationSuggestion] = []

    for src_brief in source_notes:
        src_note = note_map.get(str(src_brief.id))
        if not src_note:
            continue

        src_kps = _split_knowledge_points(src_note.knowledge_points)
        src_is_mistake = src_note.type == "mistake"

        for tgt_brief in source_notes:
            if tgt_brief.id == src_brief.id:
                continue
            tgt_note = note_map.get(str(tgt_brief.id))
            if not tgt_note:
                continue

            tgt_kps = _split_knowledge_points(tgt_note.knowledge_points)
            kp_overlap, kp_matched = _kp_overlap_score(src_kps, tgt_kps)
            subj_match = _subject_match(src_note.subject, tgt_note.subject)

            score = 0.0
            relation_type: RelationType | None = None

            if src_is_mistake and tgt_note.type == "note" and (subj_match or kp_overlap > 0):
                relation_type = RelationType.explains
                score = (3.0 if subj_match else 0) + kp_overlap * 2.0

            elif src_note.type == "note" and tgt_note.type == "mistake" and (subj_match or kp_overlap > 0):
                relation_type = RelationType.explains
                score = (3.0 if subj_match else 0) + kp_overlap * 2.0

            elif src_is_mistake and tgt_note.type == "mistake" and (subj_match or kp_overlap > 0):
                relation_type = RelationType.similar
                score = (2.0 if subj_match else 0) + kp_overlap * 2.5

            elif src_note.type == "note" and tgt_note.type == "note" and kp_overlap > 0:
                relation_type = RelationType.source_for
                score = kp_overlap * 2.0

            if relation_type and score > 0:
                reason = _explain_relation(src_note, tgt_note, relation_type, kp_matched, subj_match)
                suggestions.append(RelationSuggestion(
                    source_type=SourceType.mistake if src_is_mistake else SourceType.note,
                    source_id=str(src_note.id),
                    target_type=SourceType.mistake if tgt_note.type == "mistake" else SourceType.note,
                    target_id=str(tgt_note.id),
                    relation_type=relation_type,
                    score=round(min(score / 10.0, 1.0), 2),
                    reason=reason,
                    status=RelationStatus.suggested,
                ))

    suggestions.sort(key=lambda s: s.score, reverse=True)
    seen: set[tuple[str, str, str]] = set()
    unique: list[RelationSuggestion] = []
    for s in suggestions:
        key = (s.source_id, s.target_id, s.relation_type.value)
        if key not in seen:
            seen.add(key)
            unique.append(s)
        if len(unique) >= limit:
            break

    return unique
