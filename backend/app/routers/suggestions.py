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
            tag_result = await db.execute(select(Tag).where(Tag.name == req.tag))
            tag = tag_result.scalar_one_or_none()
            if not tag:
                tag = Tag(name=req.tag)
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
