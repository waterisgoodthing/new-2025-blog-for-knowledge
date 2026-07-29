import unittest
import uuid
from datetime import timedelta
from tempfile import TemporaryDirectory
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock

from fastapi.routing import APIRoute
from sqlalchemy import func, select
from sqlalchemy.exc import SQLAlchemyError

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
from app.services.dashboard_service import get_dashboard_summary, map_database_health, map_storage_health
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


def test_dashboard_empty_sections_map_to_healthy_system_status():
    assert map_database_health("empty", "empty") == "ok"
    assert map_storage_health("empty") == "ok"
    assert map_database_health("unavailable", "ready") == "unavailable"
    assert map_storage_health("unknown") == "unknown"


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
        self.assertEqual(summary.sections.learning, "ready")
        self.assertEqual(summary.sections.activity, "ready")
        self.assertEqual(summary.sections.storage, "ready")



class DashboardFailureMatrixTest(unittest.IsolatedAsyncioTestCase):
    @staticmethod
    def _counts_result():
        return SimpleNamespace(one=lambda: SimpleNamespace(_mapping={
            "questions": 0,
            "mistakes": 0,
            "knowledge_points": 0,
            "due_reviews": 0,
        }))

    @staticmethod
    def _empty_result():
        return SimpleNamespace(
            scalars=lambda: SimpleNamespace(all=lambda: []),
            all=lambda: [],
        )

    async def test_learning_failure_keeps_activity_and_storage_independent(self):
        empty_result = self._empty_result()
        session = SimpleNamespace(
            execute=AsyncMock(side_effect=[SQLAlchemyError("learning offline"), empty_result, empty_result, empty_result]),
            scalar=AsyncMock(return_value=0),
            rollback=AsyncMock(),
        )

        summary = await get_dashboard_summary(session, upload_root=Path("/tmp"))

        self.assertEqual(summary.sections.learning, "unavailable")
        self.assertEqual(summary.sections.activity, "empty")
        self.assertEqual(summary.sections.storage, "empty")
        self.assertEqual(summary.system.database, "unavailable")
        self.assertEqual(summary.system.storage, "ok")
        self.assertEqual(session.rollback.await_count, 1)

    async def test_activity_failure_keeps_learning_and_storage_independent(self):
        session = SimpleNamespace(
            execute=AsyncMock(side_effect=[self._counts_result(), SQLAlchemyError("activity offline")]),
            scalar=AsyncMock(return_value=0),
            rollback=AsyncMock(),
        )

        summary = await get_dashboard_summary(session, upload_root=Path("/tmp"))

        self.assertEqual(summary.sections.learning, "empty")
        self.assertEqual(summary.sections.activity, "unavailable")
        self.assertEqual(summary.sections.storage, "empty")
        self.assertEqual(summary.system.database, "unavailable")
        self.assertEqual(summary.system.storage, "ok")
        self.assertEqual(session.rollback.await_count, 1)

    async def test_storage_failure_keeps_learning_and_activity_independent(self):
        empty_result = self._empty_result()
        session = SimpleNamespace(
            execute=AsyncMock(side_effect=[self._counts_result(), empty_result, empty_result, empty_result]),
            scalar=AsyncMock(side_effect=SQLAlchemyError("storage offline")),
            rollback=AsyncMock(),
        )

        summary = await get_dashboard_summary(session, upload_root=Path("/tmp"))

        self.assertEqual(summary.sections.learning, "empty")
        self.assertEqual(summary.sections.activity, "empty")
        self.assertEqual(summary.sections.storage, "unknown")
        self.assertEqual(summary.system.database, "ok")
        self.assertEqual(summary.system.storage, "unknown")
        self.assertEqual(session.rollback.await_count, 1)
