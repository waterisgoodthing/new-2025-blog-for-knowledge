import uuid
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.note import Note, Tag, User, note_tags
from app.models.folder import Folder
from app.routers.auth import get_current_admin
from app.schemas.knowledge_assistant import (
    ExecuteSuggestionRequest,
    SuggestionListResponse,
)
from app.services.knowledge_assistant import generate_suggestions

WEEKLY_FOLDER_NAME = "周度总结"

router = APIRouter(prefix="/api/ai", tags=["ai"])


@router.get("/suggestions", response_model=SuggestionListResponse)
async def get_suggestions(
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(get_current_admin),
):
    suggestions = await generate_suggestions(db)
    return SuggestionListResponse(suggestions=suggestions)


@router.post("/suggestions/execute")
async def execute_suggestion(
    req: ExecuteSuggestionRequest,
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(get_current_admin),
):
    executed = 0
    failed = 0
    errors: list[str] = []

    if req.action == "add_tag" and req.tag:
        for slug in req.targets:
            result = await db.execute(select(Note).where(Note.slug == slug))
            note = result.scalar_one_or_none()
            if not note:
                failed += 1
                errors.append(f"Note {slug} not found")
                continue
            from app.services.tag_canonicalization import canonicalize_tag
            canonical_name = canonicalize_tag(req.tag)
            if not canonical_name:
                failed += 1
                errors.append(f"Tag '{req.tag}' filtered as low-value")
                continue
            tag_result = await db.execute(select(Tag).where(Tag.name == canonical_name))
            tag = tag_result.scalar_one_or_none()
            if not tag:
                tag = Tag(name=canonical_name)
                db.add(tag)
                await db.flush()
            if tag not in note.tags:
                note.tags.append(tag)
            executed += 1

    elif req.action == "move_to_folder" and req.folder_id:
        folder_uuid = uuid.UUID(req.folder_id)
        folder = await db.get(Folder, folder_uuid)
        if not folder:
            raise HTTPException(status_code=404, detail="Folder not found")
        for slug in req.targets:
            result = await db.execute(select(Note).where(Note.slug == slug))
            note = result.scalar_one_or_none()
            if not note:
                failed += 1
                continue
            note.folder_id = folder_uuid
            executed += 1

    else:
        raise HTTPException(status_code=400, detail=f"Unsupported action: {req.action}")

    return {"executed": executed, "failed": failed, "errors": errors}


@router.get("/weekly-summary")
async def get_weekly_summary(
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(get_current_admin),
):
    now = datetime.utcnow()
    week_start = now - timedelta(days=7)

    new_notes = await db.execute(
        select(func.count()).where(Note.created_at >= week_start).where(Note.type != "mistake")
    )
    new_mistakes = await db.execute(
        select(func.count()).where(Note.created_at >= week_start).where(Note.type == "mistake")
    )
    reviewed = await db.execute(
        select(func.count()).where(Note.last_reviewed >= week_start).where(Note.type == "mistake")
    )
    subjects = await db.execute(
        select(Note.subject, func.count().label("count"))
        .where(Note.type == "mistake")
        .where(Note.created_at >= week_start)
        .where(Note.subject.isnot(None))
        .group_by(Note.subject)
        .order_by(func.count().desc())
        .limit(5)
    )

    kp_rows = await db.execute(
        select(Note.knowledge_points)
        .where(Note.type == "mistake")
        .where(Note.created_at >= week_start)
        .where(Note.knowledge_points.isnot(None))
        .where(Note.knowledge_points != "")
    )
    kp_counts: dict[str, int] = {}
    for (kp_str,) in kp_rows.all():
        for part in kp_str.replace("，", ",").replace("、", ",").split(","):
            key = part.strip()
            if key:
                kp_counts[key] = kp_counts.get(key, 0) + 1
    top_kp = sorted(kp_counts.items(), key=lambda x: x[1], reverse=True)[:5]

    return {
        "week_start": week_start.isoformat(),
        "week_end": now.isoformat(),
        "new_notes": new_notes.scalar() or 0,
        "new_mistakes": new_mistakes.scalar() or 0,
        "reviewed_count": reviewed.scalar() or 0,
        "top_subjects": [{"subject": r.subject, "count": r.count} for r in subjects.all()],
        "top_knowledge_points": [{"name": name, "count": count} for name, count in top_kp],
    }


@router.post("/weekly-summary/generate")
async def generate_weekly_summary(
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(get_current_admin),
):
    now = datetime.utcnow()
    days_since_monday = now.weekday()
    week_start = (now - timedelta(days=days_since_monday)).replace(hour=0, minute=0, second=0, microsecond=0)
    week_slug = f"weekly-{week_start.strftime('%Y%m%d')}"
    week_label = f"{week_start.strftime('%m-%d')} ~ {now.strftime('%m-%d')}"

    folder_result = await db.execute(select(Folder).where(Folder.name == WEEKLY_FOLDER_NAME))
    folder = folder_result.scalar_one_or_none()
    if not folder:
        folder = Folder(name=WEEKLY_FOLDER_NAME)
        db.add(folder)
        await db.flush()

    new_notes_r = await db.execute(
        select(func.count()).where(Note.created_at >= week_start).where(Note.type != "mistake")
    )
    new_mistakes_r = await db.execute(
        select(func.count()).where(Note.created_at >= week_start).where(Note.type == "mistake")
    )
    reviewed_r = await db.execute(
        select(func.count()).where(Note.last_reviewed >= week_start).where(Note.type == "mistake")
    )
    subjects_r = await db.execute(
        select(Note.subject, func.count().label("count"))
        .where(Note.type == "mistake")
        .where(Note.created_at >= week_start)
        .where(Note.subject.isnot(None))
        .group_by(Note.subject)
        .order_by(func.count().desc())
        .limit(5)
    )

    kp_rows = await db.execute(
        select(Note.knowledge_points)
        .where(Note.type == "mistake")
        .where(Note.created_at >= week_start)
        .where(Note.knowledge_points.isnot(None))
        .where(Note.knowledge_points != "")
    )
    kp_counts: dict[str, int] = {}
    for (kp_str,) in kp_rows.all():
        for part in kp_str.replace("，", ",").replace("、", ",").split(","):
            key = part.strip()
            if key:
                kp_counts[key] = kp_counts.get(key, 0) + 1
    top_kp = sorted(kp_counts.items(), key=lambda x: x[1], reverse=True)[:5]

    content_lines = [
        f"# 周度学习总结 ({week_label})",
        "",
        "## 本周数据",
        f"- 新增笔记: {new_notes_r.scalar() or 0} 篇",
        f"- 新增错题: {new_mistakes_r.scalar() or 0} 道",
        f"- 复习完成: {reviewed_r.scalar() or 0} 道",
        "",
    ]
    subjects = subjects_r.all()
    if subjects:
        content_lines.append("## 主要科目")
        for s in subjects:
            content_lines.append(f"- {s.subject}: {s.count} 道错题")
        content_lines.append("")
    if top_kp:
        content_lines.append("## 高频知识点")
        for name, count in top_kp:
            content_lines.append(f"- {name}: {count} 次")
        content_lines.append("")

    content = "\n".join(content_lines)
    title = f"周度学习总结 ({week_label})"

    existing = await db.execute(select(Note).where(Note.slug == week_slug))
    note = existing.scalar_one_or_none()
    if note:
        note.title = title
        note.content = content
        note.folder_id = folder.id
        action = "updated"
    else:
        note = Note(
            slug=week_slug,
            title=title,
            content=content,
            type="note",
            status="published",
            folder_id=folder.id,
        )
        db.add(note)
        action = "created"

    tag_names = ["周度总结", "自动生成"]
    for tag_name in tag_names:
        tag_result = await db.execute(select(Tag).where(Tag.name == tag_name))
        tag = tag_result.scalar_one_or_none()
        if not tag:
            tag = Tag(name=tag_name)
            db.add(tag)
            await db.flush()
        if tag not in note.tags:
            note.tags.append(tag)

    await db.commit()
    return {"action": action, "slug": week_slug, "folder_id": str(folder.id)}
