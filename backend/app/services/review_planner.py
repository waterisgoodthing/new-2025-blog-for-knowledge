from __future__ import annotations

from collections import Counter, defaultdict
from datetime import date, timedelta
from typing import Iterable

from app.models.note import Note
from app.schemas.note import ReviewPlan, ReviewSubjectSummary, ReviewWeaknessItem


def _split_knowledge_points(value: str | None) -> list[str]:
    if not value:
        return []
    normalized = value.replace("，", ",").replace("、", ",").replace("\n", ",")
    return [item.strip() for item in normalized.split(",") if item.strip()]


def build_review_plan(mistakes: Iterable[Note], today: date | None = None) -> ReviewPlan:
    today = today or date.today()
    week_end = today + timedelta(days=7)
    items = list(mistakes)

    due_today = [item for item in items if item.next_review and item.next_review <= today]
    overdue = [item for item in items if item.next_review and item.next_review < today]
    week_items = [item for item in items if item.next_review and today <= item.next_review <= week_end]
    next_dates = sorted(item.next_review for item in items if item.next_review and item.next_review > today)

    by_subject: dict[str, list[Note]] = defaultdict(list)
    for item in items:
        by_subject[item.subject or "未分类"].append(item)

    subject_summaries = [
        ReviewSubjectSummary(
            subject=subject,
            total=len(subject_items),
            due_today=sum(1 for item in subject_items if item.next_review and item.next_review <= today),
            hard=sum(1 for item in subject_items if item.difficulty == "hard"),
            average_ef=round(sum((item.ef or 2.5) for item in subject_items) / len(subject_items), 2),
        )
        for subject, subject_items in by_subject.items()
    ]
    subject_summaries.sort(key=lambda item: (item.due_today, item.hard, item.total), reverse=True)

    point_counts: Counter[str] = Counter()
    point_due_counts: Counter[str] = Counter()
    point_subjects: dict[str, set[str]] = defaultdict(set)
    for item in items:
        points = _split_knowledge_points(item.knowledge_points)
        for point in points:
            point_counts[point] += 1
            if item.next_review and item.next_review <= today:
                point_due_counts[point] += 1
            point_subjects[point].add(item.subject or "未分类")

    weaknesses = [
        ReviewWeaknessItem(
            name=name,
            count=count,
            due_today=point_due_counts[name],
            subjects=sorted(point_subjects[name]),
        )
        for name, count in point_counts.most_common(8)
    ]

    recommendations: list[str] = []
    if due_today:
        recommendations.append(f"今天优先复习 {len(due_today)} 道到期错题，先处理最早到期和 hard 难度。")
    else:
        recommendations.append("今天没有到期错题，可以选择 1 道高频知识点错题做主动回顾。")
    if weaknesses:
        recommendations.append(f"本周重点回看“{weaknesses[0].name}”，它在错题中出现 {weaknesses[0].count} 次。")
    if subject_summaries:
        recommendations.append(f"当前最需要关注的科目是“{subject_summaries[0].subject}”。")

    return ReviewPlan(
        today_count=len(due_today),
        overdue_count=len(overdue),
        week_count=len(week_items),
        next_review_date=next_dates[0] if next_dates else None,
        subject_summaries=subject_summaries[:6],
        weaknesses=weaknesses,
        recommendations=recommendations,
    )
