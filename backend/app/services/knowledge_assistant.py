from datetime import datetime
from typing import Any

from sqlalchemy import func, select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.note import Note, Tag


async def query_recent_notes(db: AsyncSession, days: int = 7, limit: int = 10) -> list[dict]:
    from datetime import timedelta
    cutoff = datetime.utcnow() - timedelta(days=days)
    result = await db.execute(
        select(Note.slug, Note.title, Note.type, Note.updated_at)
        .where(Note.updated_at >= cutoff)
        .order_by(Note.updated_at.desc())
        .limit(limit)
    )
    return [{"slug": r.slug, "title": r.title, "type": r.type, "updated_at": r.updated_at.isoformat()} for r in result.all()]


async def query_untagged_notes(db: AsyncSession, limit: int = 10) -> list[dict]:
    from app.models.note import note_tags
    subq = select(note_tags.c.note_id).scalar_subquery()
    result = await db.execute(
        select(Note.slug, Note.title, Note.type)
        .where(~Note.id.in_(subq))
        .where(Note.status == "published")
        .order_by(Note.updated_at.desc())
        .limit(limit)
    )
    return [{"slug": r.slug, "title": r.title, "type": r.type} for r in result.all()]


async def query_unfoldered_notes(db: AsyncSession, limit: int = 10) -> list[dict]:
    result = await db.execute(
        select(Note.slug, Note.title, Note.type)
        .where(Note.folder_id.is_(None))
        .where(Note.status == "published")
        .order_by(Note.updated_at.desc())
        .limit(limit)
    )
    return [{"slug": r.slug, "title": r.title, "type": r.type} for r in result.all()]


async def aggregate_weaknesses(db: AsyncSession, limit: int = 5) -> list[dict]:
    by_subject = await db.execute(
        select(Note.subject, func.count().label("count"))
        .where(Note.type == "mistake")
        .where(Note.subject.isnot(None))
        .where(Note.subject != "")
        .group_by(Note.subject)
        .order_by(func.count().desc())
        .limit(limit)
    )
    results: list[dict] = [{"name": r.subject, "count": r.count, "source": "subject"} for r in by_subject.all()]

    kp_rows = await db.execute(
        select(Note.knowledge_points)
        .where(Note.type == "mistake")
        .where(Note.knowledge_points.isnot(None))
        .where(Note.knowledge_points != "")
    )
    kp_counts: dict[str, int] = {}
    for (kp_str,) in kp_rows.all():
        for part in kp_str.replace("，", ",").replace("、", ",").split(","):
            key = part.strip()
            if key:
                kp_counts[key] = kp_counts.get(key, 0) + 1
    for name, count in sorted(kp_counts.items(), key=lambda x: x[1], reverse=True)[:limit]:
        if not any(x["name"] == name for x in results):
            results.append({"name": name, "count": count, "source": "knowledge_points"})

    results.sort(key=lambda x: x["count"], reverse=True)
    return results[:limit]


SUGGESTION_TEMPLATES = {
    "tag": "「{title}」没有标签，建议添加标签便于检索。",
    "folder": "「{title}」未归档到文件夹，建议归入合适的文件夹。",
    "weakness": "「{subject}」累计 {count} 道错题，建议重点复习。",
    "recent": "本周新增了 {count} 篇内容，建议整理到文件夹以保持有序。",
}


async def generate_suggestions(db: AsyncSession) -> list[dict[str, Any]]:
    suggestions: list[dict[str, Any]] = []

    untagged = await query_untagged_notes(db, limit=5)
    for item in untagged[:3]:
        suggestions.append({
            "type": "tag",
            "title": f"建议为「{item['title']}」添加标签",
            "description": SUGGESTION_TEMPLATES["tag"].format(title=item["title"]),
            "targets": [item["slug"]],
            "action": "add_tag",
            "reason": "缺少标签会影响检索效率",
        })

    unfoldered = await query_unfoldered_notes(db, limit=5)
    if len(unfoldered) >= 3:
        suggestions.append({
            "type": "folder",
            "title": f"{len(unfoldered)} 篇内容未归档",
            "description": SUGGESTION_TEMPLATES["folder"].format(title=f"{len(unfoldered)} 篇笔记"),
            "targets": [n["slug"] for n in unfoldered[:5]],
            "action": "move_to_folder",
            "reason": "未归档内容会堆积在收件箱",
        })

    weaknesses = await aggregate_weaknesses(db, limit=3)
    for w in weaknesses:
        if w["count"] >= 3:
            suggestions.append({
                "type": "review",
                "title": f"「{w['name']}」薄弱点",
                "description": SUGGESTION_TEMPLATES["weakness"].format(subject=w["name"], count=w["count"]),
                "targets": [],
                "action": "review_subject",
                "reason": f"该{'科目' if w.get('source') == 'subject' else '知识点'}累计 {w['count']} 道错题",
            })

    recent = await query_recent_notes(db, days=7)
    if recent:
        suggestions.append({
            "type": "activity",
            "title": f"本周新增 {len(recent)} 篇内容",
            "description": SUGGESTION_TEMPLATES["recent"].format(count=len(recent)),
            "targets": [r["slug"] for r in recent],
            "action": "organize",
            "reason": "定期整理有助于保持知识库有序",
        })

    return suggestions
