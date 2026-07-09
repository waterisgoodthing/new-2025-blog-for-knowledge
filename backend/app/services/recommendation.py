import json
from datetime import date, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.note import Note
from app.models.recommendation import DailyRecommendation
from app.services.ai_prompt_registry import build_text_messages
from app.services.ai_task_types import AiTaskType


async def collect_context(db: AsyncSession) -> str:
    sections = []

    result = await db.execute(
        select(Note)
        .options(selectinload(Note.tags))
        .where(Note.hidden == False)
        .order_by(Note.updated_at.desc())
        .limit(5)
    )
    recent_notes = result.scalars().all()
    if recent_notes:
        lines = [f"- [{n.title}] type={n.type} slug={n.slug}" for n in recent_notes]
        sections.append("最近笔记:\n" + "\n".join(lines))

    result = await db.execute(
        select(Note)
        .where(Note.type == "mistake")
        .where(Note.hidden == False)
        .order_by(Note.updated_at.desc())
        .limit(5)
    )
    recent_mistakes = result.scalars().all()
    if recent_mistakes:
        lines = [f"- [{m.title}] subject={m.subject} difficulty={m.difficulty}" for m in recent_mistakes]
        sections.append("最近错题:\n" + "\n".join(lines))

    today = date.today()
    result = await db.execute(
        select(Note)
        .where(Note.type == "mistake")
        .where(Note.next_review <= today)
        .order_by(Note.next_review.asc())
        .limit(5)
    )
    due_mistakes = result.scalars().all()
    if due_mistakes:
        lines = [f"- [{m.title}] review after {m.interval} days" for m in due_mistakes]
        sections.append("今日待复习错题:\n" + "\n".join(lines))

    result = await db.execute(
        select(Note)
        .where(Note.type == "mistake")
        .where(Note.knowledge_points.isnot(None))
        .where(Note.knowledge_points != "")
        .order_by(Note.updated_at.desc())
        .limit(10)
    )
    mistakes_with_kp = result.scalars().all()
    if mistakes_with_kp:
        kp_list = [m.knowledge_points for m in mistakes_with_kp if m.knowledge_points]
        sections.append("错题知识点:\n" + "\n".join(f"- {kp}" for kp in kp_list[:5]))

    try:
        import importlib.resources
        from pathlib import Path

        share_json = Path(__file__).resolve().parent.parent.parent.parent / "src" / "app" / "share" / "list.json"
        if share_json.exists():
            share_data = json.loads(share_json.read_text())
            items = share_data[:10]
            lines = [f"- [{s['name']}] {s.get('description', '')[:50]}" for s in items]
            sections.append("分享资源:\n" + "\n".join(lines))
    except Exception:
        pass

    return "\n\n".join(sections) if sections else "暂无足够上下文，建议推荐写一篇新笔记。"


async def call_llm(context: str) -> dict | None:
    from app.services.ai_gateway import call_general

    user_prompt = f"用户学习上下文：\n\n{context}\n\n请推荐今天最值得关注的一项内容。"

    try:
        messages = build_text_messages(AiTaskType.RECOMMENDATION, user_prompt)
        gw = await call_general(AiTaskType.RECOMMENDATION, messages)
        if not gw.success or not isinstance(gw.data, dict):
            return None
        return gw.data
    except Exception:
        return None


def _normalize(raw: dict, today: date) -> dict:
    rec_type = raw.get("type", "note")
    if rec_type not in ("note", "mistake", "review", "resource", "music", "podcast"):
        rec_type = "note"

    return {
        "date": today,
        "title": raw.get("title", "今日学习推荐"),
        "type": rec_type,
        "reason": raw.get("reason", "根据你的学习情况推荐"),
        "target": raw.get("target"),
        "action_label": raw.get("actionLabel", "查看详情"),
        "source": raw.get("source"),
        "raw_context": json.dumps(raw, ensure_ascii=False),
    }


async def get_or_create_today_recommendation(db: AsyncSession) -> dict:
    today = date.today()

    result = await db.execute(
        select(DailyRecommendation).where(DailyRecommendation.date == today)
    )
    existing = result.scalar_one_or_none()
    if existing:
        return {
            "date": existing.date,
            "title": existing.title,
            "type": existing.type,
            "reason": existing.reason,
            "target": existing.target,
            "action_label": existing.action_label,
            "source": existing.source,
        }

    context = await collect_context(db)
    raw = await call_llm(context)

    if raw:
        normalized = _normalize(raw, today)
        normalized["raw_context"] = context
    else:
        yesterday = today - timedelta(days=1)
        fallback_result = await db.execute(
            select(DailyRecommendation)
            .where(DailyRecommendation.date == yesterday)
            .order_by(DailyRecommendation.created_at.desc())
            .limit(1)
        )
        fallback = fallback_result.scalar_one_or_none()
        if fallback:
            normalized = {
                "date": today,
                "title": fallback.title,
                "type": fallback.type,
                "reason": fallback.reason,
                "target": fallback.target,
                "action_label": fallback.action_label,
                "source": fallback.source,
                "raw_context": context,
            }
        else:
            normalized = {
                "date": today,
                "title": "写一篇新笔记",
                "type": "note",
                "reason": "今天还没有学习记录，开始记录你的学习心得吧。",
                "target": None,
                "action_label": "开始写作",
                "source": None,
                "raw_context": context,
            }

    rec = DailyRecommendation(**normalized)
    db.add(rec)
    await db.flush()

    return {
        "date": rec.date,
        "title": rec.title,
        "type": rec.type,
        "reason": rec.reason,
        "target": rec.target,
        "action_label": rec.action_label,
        "source": rec.source,
    }
