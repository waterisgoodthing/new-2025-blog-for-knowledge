from __future__ import annotations

from collections import Counter, defaultdict
from datetime import date, datetime, timedelta, timezone

from sqlalchemy import Select, and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.note import Note, Tag, note_tags
from app.schemas.knowledge import (
    ContextPackRequest,
    ContextPackResponse,
    ContextPackStats,
    DateRange,
    NoteBrief,
    ReviewStateFilter,
    SourceRef,
    SourceType,
    WeakPointItem,
    WeakPointsResponse,
)


def _split_knowledge_points(value: str | None) -> list[str]:
    if not value:
        return []
    normalized = value.replace("，", ",").replace("、", ",").replace("\n", ",").replace("；", ",")
    return [item.strip() for item in normalized.split(",") if item.strip()]


def _build_source_ref(
    note: Note,
    source_type: SourceType,
    field_name: str,
    excerpt: str,
    confidence: float,
    match_reasons: list[str],
) -> SourceRef:
    url = f"/notes/{note.slug}" if source_type == SourceType.note else f"/notes/{note.slug}"
    return SourceRef(
        source_type=source_type,
        source_id=str(note.id),
        title=note.title or "",
        slug=note.slug or "",
        field=field_name,
        excerpt=excerpt[:300] if excerpt else "",
        url=url,
        confidence=round(confidence, 2),
        match_reasons=match_reasons,
    )


def _compute_relevance_score(
    note: Note,
    subject: str | None,
    kp_keywords: list[str],
    tag_names: list[str],
    type_filter: str | None,
    review_state: ReviewStateFilter | None,
    today: date,
) -> tuple[float, list[str]]:
    score = 0.0
    reasons: list[str] = []

    if subject and note.subject:
        if note.subject.strip().lower() == subject.strip().lower():
            score += 3
            reasons.append("subject_match")

    if kp_keywords and note.knowledge_points:
        note_kps = _split_knowledge_points(note.knowledge_points)
        overlap = 0
        for kw in kp_keywords:
            for nkp in note_kps:
                if kw.lower() in nkp.lower() or nkp.lower() in kw.lower():
                    overlap += 1
                    break
        if overlap > 0:
            score += overlap * 4
            reasons.append("knowledge_point_overlap")

    if tag_names and note.tags:
        note_tag_names = [t.name.lower() for t in note.tags]
        tag_overlap = sum(1 for tn in tag_names if tn.lower() in note_tag_names)
        if tag_overlap > 0:
            score += tag_overlap * 2
            reasons.append("tag_overlap")

    if type_filter and note.type == type_filter:
        score += 1
        reasons.append("type_match")

    if note.type == "mistake":
        if note.next_review and note.next_review <= today:
            score += 2
            reasons.append("due_review_bonus")

        if note.updated_at:
            days_since_update = (datetime.now(timezone.utc) - note.updated_at.replace(tzinfo=timezone.utc)).days
            if days_since_update <= 7:
                score += 2
                reasons.append("recent_mistake_bonus")
            elif days_since_update > 90:
                score -= 1
                reasons.append("stale_penalty")

    return score, reasons


async def retrieve_context_pack(
    db: AsyncSession,
    request: ContextPackRequest,
) -> ContextPackResponse:
    today = date.today()

    query: Select = select(Note).options(selectinload(Note.tags))

    if request.subject:
        query = query.where(Note.subject.ilike(f"%{request.subject.strip()}%"))

    if request.type:
        query = query.where(Note.type == request.type)

    if request.difficulty:
        query = query.where(Note.difficulty == request.difficulty)

    if request.knowledge_points:
        kp_conditions = []
        for kp in request.knowledge_points[:5]:
            kp_conditions.append(Note.knowledge_points.ilike(f"%{kp.strip()}%"))
        if kp_conditions:
            query = query.where(or_(*kp_conditions))

    if request.tags:
        tag_sub = (
            select(note_tags.c.note_id)
            .join(Tag, Tag.id == note_tags.c.tag_id)
            .where(or_(*[Tag.name.ilike(f"%{t.strip()}%") for t in request.tags]))
            .scalar_subquery()
        )
        query = query.where(Note.id.in_(tag_sub))

    if request.date_range:
        dr: DateRange = request.date_range
        if dr.from_date:
            query = query.where(Note.created_at >= datetime.combine(dr.from_date, datetime.min.time()))
        if dr.to_date:
            query = query.where(Note.created_at <= datetime.combine(dr.to_date, datetime.max.time()))

    if request.review_state == ReviewStateFilter.due:
        query = query.where(Note.next_review <= today)
    elif request.review_state == ReviewStateFilter.overdue:
        query = query.where(Note.next_review < today)
    elif request.review_state == ReviewStateFilter.upcoming:
        week_end = today + timedelta(days=7)
        query = query.where(and_(Note.next_review >= today, Note.next_review <= week_end))

    query = query.order_by(Note.updated_at.desc()).limit(request.limit * 3)
    result = await db.execute(query)
    notes = list(result.scalars().all())

    kp_keywords = request.knowledge_points or []
    tag_names = request.tags or []

    scored: list[tuple[Note, float, list[str]]] = []
    for note in notes:
        score, reasons = _compute_relevance_score(
            note, request.subject, kp_keywords, tag_names,
            request.type, request.review_state, today,
        )
        scored.append((note, score, reasons))

    scored.sort(key=lambda x: x[1], reverse=True)
    top_notes = scored[:request.limit]

    sources: list[SourceRef] = []
    related_notes: list[NoteBrief] = []
    related_mistakes: list[NoteBrief] = []
    mistake_count = 0
    note_count = 0
    error_reason_counter: Counter[str] = Counter()

    for note, score, reasons in top_notes:
        excerpt = ""
        field_name = "content"
        if note.type == "mistake":
            excerpt = note.analysis or note.question or note.content or ""
            field_name = "analysis"
            mistake_count += 1
        else:
            excerpt = (note.summary or note.content or "")[:300]
            field_name = "content"
            note_count += 1

        source_ref = _build_source_ref(
            note,
            SourceType.mistake if note.type == "mistake" else SourceType.note,
            field_name,
            excerpt,
            min(score / 10.0, 1.0),
            reasons,
        )
        sources.append(source_ref)

        brief = NoteBrief(
            id=note.id,
            slug=note.slug,
            title=note.title,
            type=note.type,
            subject=note.subject,
            knowledge_points=note.knowledge_points,
            difficulty=note.difficulty,
            summary=note.summary,
            updated_at=note.updated_at,
        )

        if note.type == "mistake":
            related_mistakes.append(brief)
            if note.ai_metadata and isinstance(note.ai_metadata, dict):
                er = note.ai_metadata.get("error_reason", "")
                if er:
                    error_reason_counter[er] += 1
        else:
            related_notes.append(brief)

    top_error_reasons = [reason for reason, _ in error_reason_counter.most_common(5)]

    stats = ContextPackStats(
        mistake_count=mistake_count,
        note_count=note_count,
        top_error_reasons=top_error_reasons,
    )

    return ContextPackResponse(
        sources=sources,
        related_notes=related_notes,
        related_mistakes=related_mistakes,
        suggested_relations=[],
        stats=stats,
    )


async def retrieve_weak_points(
    db: AsyncSession,
    days: int = 30,
) -> WeakPointsResponse:
    today = date.today()
    cutoff = today - timedelta(days=days)

    result = await db.execute(
        select(Note)
        .options(selectinload(Note.tags))
        .where(Note.type == "mistake")
        .where(Note.updated_at >= datetime.combine(cutoff, datetime.min.time()))
    )
    mistakes = list(result.scalars().all())

    kp_map: dict[str, list[Note]] = defaultdict(list)
    for note in mistakes:
        kps = _split_knowledge_points(note.knowledge_points)
        if not kps:
            kps = [note.subject or "未分类"]
        for kp in kps:
            kp_map[kp].append(note)

    weak_points: list[WeakPointItem] = []
    for kp, notes in sorted(kp_map.items(), key=lambda x: len(x[1]), reverse=True):
        mistake_count = len(notes)
        due_review_count = sum(1 for n in notes if n.next_review and n.next_review <= today)
        recent_error_count = sum(
            1 for n in notes
            if n.updated_at and (datetime.now(timezone.utc) - n.updated_at.replace(tzinfo=timezone.utc)).days <= 7
        )

        error_reason_counter: Counter[str] = Counter()
        evidence_sources: list[SourceRef] = []
        for n in notes:
            if n.ai_metadata and isinstance(n.ai_metadata, dict):
                er = n.ai_metadata.get("error_reason", "")
                if er:
                    error_reason_counter[er] += 1
            if len(evidence_sources) < 3:
                evidence_sources.append(
                    _build_source_ref(
                        n, SourceType.mistake, "analysis",
                        (n.analysis or n.question or "")[:200],
                        0.7, ["weak_point_evidence"],
                    )
                )

        subject = notes[0].subject if notes else "未分类"

        weak_points.append(WeakPointItem(
            subject=subject or "未分类",
            knowledge_point=kp,
            mistake_count=mistake_count,
            due_review_count=due_review_count,
            recent_error_count=recent_error_count,
            top_error_reasons=[r for r, _ in error_reason_counter.most_common(3)],
            evidence_sources=evidence_sources,
        ))

    return WeakPointsResponse(days=days, weak_points=weak_points[:20])
