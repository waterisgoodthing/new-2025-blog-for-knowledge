import unittest
import uuid
from datetime import timedelta
from tempfile import TemporaryDirectory
from pathlib import Path

from fastapi.routing import APIRoute
from sqlalchemy import func, select

import main
from app.database import async_session, engine
from app.models.attachment import Attachment
from app.models.mistake import Mistake
from app.models.question import Question
from app.models.review_item import ReviewItem
from app.models.taxonomy import KnowledgePoint
from app.routers.auth import get_current_admin
from app.schemas.mistake import MistakeDraftCreate
from app.schemas.question import QuestionDraftCreate
from app.schemas.taxonomy import KnowledgePointCreate, SubjectCreate
from app.services.attachment_service import create_attachment_from_bytes
from app.services.dashboard_service import get_dashboard_summary
from app.services.draft_service import convert_question_draft, create_question_draft
from app.services.mistake_service import create_mistake_draft, convert_mistake_draft
from app.services.review_item_service import submit_review
from app.services.taxonomy_service import create_knowledge_point, create_subject


def test_dashboard_summary_route_is_registered_and_admin_only():
    route = next(
        (
            route
            for route in main.app.routes
            if isinstance(route, APIRoute)
            and route.path == "/api/admin/dashboard/summary"
            and "GET" in route.methods
        ),
        None,
    )

    assert route is not None
    assert get_current_admin in {
        dependency.call for dependency in route.dependant.dependencies
    }


class DashboardSummaryServiceTest(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.session = async_session()
        self.addAsyncCleanup(engine.dispose)
        self.addAsyncCleanup(self.session.close)
        self.addAsyncCleanup(self.session.rollback)
        await self.session.begin()
        self.tmp = TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)

    async def test_summary_returns_bounded_real_counts_and_recent_activity(self):
        baseline = {
            "questions": await self.session.scalar(
                select(func.count()).select_from(Question).where(Question.status == "active")
            ),
            "mistakes": await self.session.scalar(
                select(func.count()).select_from(Mistake).where(Mistake.status == "active")
            ),
            "knowledge_points": await self.session.scalar(
                select(func.count()).select_from(KnowledgePoint).where(KnowledgePoint.status == "active")
            ),
            "attachments": await self.session.scalar(
                select(func.count()).select_from(Attachment).where(Attachment.status == "active")
            ),
        }
        suffix = uuid.uuid4().hex[:8]
        subject = await create_subject(
            self.session,
            SubjectCreate(name=f"Dashboard {suffix}"),
        )
        knowledge_point = await create_knowledge_point(
            self.session,
            KnowledgePointCreate(subject_id=subject.id, name=f"Point {suffix}"),
        )
        question_draft = await create_question_draft(
            self.session,
            QuestionDraftCreate(
                subject_id=subject.id,
                question_text=f"Dashboard question {suffix}?",
                question_type="short_answer",
                correct_answer="Answer",
                knowledge_point_ids=[knowledge_point.id],
            ),
        )
        question = await convert_question_draft(
            self.session,
            question_draft.item.id,
            version=1,
        )
        mistake_draft = await create_mistake_draft(
            self.session,
            MistakeDraftCreate(
                question_id=question.id,
                mistake_reason="Missed a condition",
            ),
        )
        mistake = await convert_mistake_draft(
            self.session,
            mistake_draft.item.id,
            version=1,
        )
        review_item = await self.session.get(ReviewItem, mistake.review_item_id)
        reviewed_at = review_item.next_review_at + timedelta(minutes=1)
        _item, record = await submit_review(
            self.session,
            review_item.id,
            rating=4,
            expected_next_review_at=review_item.next_review_at,
            now=reviewed_at,
        )
        await create_attachment_from_bytes(
            self.session,
            original_name="dashboard-proof.txt",
            content=b"proof",
            mime_type="text/plain",
            upload_root=Path(self.tmp.name),
        )

        summary = await get_dashboard_summary(
            self.session,
            upload_root=Path(self.tmp.name),
            now=reviewed_at,
        )

        self.assertEqual(summary.counts.questions, baseline["questions"] + 1)
        self.assertEqual(summary.counts.mistakes, baseline["mistakes"] + 1)
        self.assertEqual(summary.counts.knowledge_points, baseline["knowledge_points"] + 1)
        self.assertEqual(summary.counts.attachments, baseline["attachments"] + 1)
        self.assertLessEqual(len(summary.recent_questions), 5)
        self.assertLessEqual(len(summary.recent_mistakes), 5)
        self.assertLessEqual(len(summary.recent_reviews), 5)
        self.assertIn(question.id, {item.id for item in summary.recent_questions})
        self.assertIn(mistake.id, {item.id for item in summary.recent_mistakes})
        self.assertIn(record.id, {item.id for item in summary.recent_reviews})
        self.assertEqual(summary.system.service, "ok")
        self.assertEqual(summary.system.database, "ok")
        self.assertEqual(summary.system.storage, "ok")
