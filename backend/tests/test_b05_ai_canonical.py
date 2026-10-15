"""B05b/EV04: canonical AI-creation save closure.

Exercises the real ASGI router + gateway + AiRun persistence + service/DB with a
fake provider adapter (no external call) to prove:

- generation persists trusted server context before the provider result is used;
- confirmation row-locks the run, verifies actor/purpose/source/version, creates
  the MistakeDraft and binds the run in one transaction;
- replaying the identical confirmed payload returns the original draft;
- a different payload, a different actor or a changed source question conflicts;
- two concurrent unbound confirmations serialise (one creates, the other sees
  the same entity or conflicts instead of double-creating).
"""

from __future__ import annotations

import asyncio
import uuid
from unittest.mock import AsyncMock, patch

import httpx
from sqlalchemy import delete, func, select

import main
from app.database import async_session, engine
from app.models.ai_run import AiRun
from app.models.mistake import Mistake, MistakeDraft
from app.models.note import Subject, User
from app.models.question import DraftItem, Question
from app.models.taxonomy import KnowledgePoint, KnowledgePointLink
from app.routers.auth import get_current_admin
from app.schemas.question import QuestionCreate
from app.schemas.taxonomy import KnowledgePointCreate, SubjectCreate
from app.services import ai_creation_service, mistake_service
from app.services.ai_service import CallResult, ProviderAttempt
from app.services.taxonomy_service import create_knowledge_point, create_subject

CANDIDATE = {
    "interpretation_id": "abcd1234",
    "version": 1,
    "summary": "概念混淆",
    "diagnosis": "把定义记反了",
    "root_cause": "未区分充分与必要",
}


def _fake_call_result() -> CallResult:
    return CallResult(
        data=dict(CANDIDATE),
        attempts=[ProviderAttempt(provider="deepseek", model="fake-model", success=True)],
        provider_used="deepseek",
        fallback_used=False,
    )


class _State:
    def __init__(self) -> None:
        self.subject_ids: list[int] = []
        self.kp_ids: list[int] = []
        self.question_ids: list[uuid.UUID] = []
        self.draft_item_ids: list[uuid.UUID] = []
        self.run_ids: list[uuid.UUID] = []
        self.user_ids: list[uuid.UUID] = []


async def _cleanup(state: _State) -> None:
    async with async_session() as session:
        if state.question_ids:
            question_ids = list(state.question_ids)
            await session.execute(
                delete(MistakeDraft).where(MistakeDraft.question_id.in_(question_ids))
            )
            await session.execute(
                delete(DraftItem).where(DraftItem.source_id.in_([str(q) for q in question_ids]))
            )
        if state.draft_item_ids:
            await session.execute(
                delete(MistakeDraft).where(MistakeDraft.draft_item_id.in_(state.draft_item_ids))
            )
            await session.execute(delete(DraftItem).where(DraftItem.id.in_(state.draft_item_ids)))
        if state.run_ids:
            await session.execute(delete(AiRun).where(AiRun.id.in_(state.run_ids)))
        if state.question_ids:
            for qid in state.question_ids:
                await session.execute(
                    delete(KnowledgePointLink).where(KnowledgePointLink.target_id == str(qid))
                )
            await session.execute(delete(Question).where(Question.id.in_(state.question_ids)))
        if state.kp_ids:
            await session.execute(delete(KnowledgePoint).where(KnowledgePoint.id.in_(state.kp_ids)))
        if state.subject_ids:
            await session.execute(delete(Subject).where(Subject.id.in_(state.subject_ids)))
        if state.user_ids:
            await session.execute(delete(User).where(User.id.in_(state.user_ids)))
        await session.commit()


async def _seed_question(state: _State, token: str) -> tuple[uuid.UUID, int]:
    async with async_session() as session:
        subject = await create_subject(session, SubjectCreate(name=f"B05 Subject {token}"))
        kp = await create_knowledge_point(
            session, KnowledgePointCreate(subject_id=subject.id, name=f"B05 KP {token}")
        )
        question = await question_service_create(session, subject.id)
        await session.commit()
        state.subject_ids.append(subject.id)
        state.kp_ids.append(kp.id)
        state.question_ids.append(question.id)
        return question.id, kp.id


async def question_service_create(session, subject_id):
    from app.services import question_service

    return await question_service.create_question(
        session,
        QuestionCreate(
            subject_id=subject_id,
            stem_md="B05 canonical question",
            question_type="short_answer",
            answer_data={"kind": "short_answer", "value": "answer"},
        ),
    )


async def _seed_admin(state: _State, name: str) -> User:
    user = User(
        id=uuid.uuid4(), username=f"b05-{name}-{uuid.uuid4().hex[:6]}",
        password_hash="test-only", is_admin=True,
    )
    async with async_session() as session:
        session.add(user)
        await session.commit()
    state.user_ids.append(user.id)
    return user


def _override(user: User):
    async def _admin():
        return user

    return _admin


async def _http_scenario(state: _State) -> None:
    admin = await _seed_admin(state, "admin")
    other = await _seed_admin(state, "other")
    question_id, kp_id = await _seed_question(state, uuid.uuid4().hex[:8])

    main.app.dependency_overrides[get_current_admin] = _override(admin)
    try:
        await main.validate_database_readiness()
        transport = httpx.ASGITransport(app=main.app)
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            with patch(
                "app.services.ai_gateway._call_with_fallback",
                new=AsyncMock(return_value=_fake_call_result()),
            ), patch("app.services.ai_gateway._write_call_log", new=AsyncMock()):
                candidate_resp = await client.post(
                    "/api/admin/mistakes/ai-candidate",
                    json={
                        "question_id": str(question_id),
                        "my_answer": "wrong",
                        "user_error_reason": "把定义记反了",
                    },
                )
            assert candidate_resp.status_code == 200, candidate_resp.text
            body = candidate_resp.json()
            run_id = body["run_id"]
            state.run_ids.append(uuid.UUID(run_id))

            # trusted context persisted before confirmation
            async with async_session() as session:
                run = await session.get(AiRun, uuid.UUID(run_id))
                assert run.creation_context["purpose"] == ai_creation_service.PURPOSE_CANONICAL_MISTAKE_DRAFT
                assert run.creation_context["source_question_id"] == str(question_id)
                assert run.creation_context["source_question_version"] == 1
                assert run.created_by == admin.id
                assert run.output_data is not None

            confirm_body = {
                "run_id": run_id,
                "review_revision": body["review_revision"],
                "question_id": str(question_id),
                "my_answer": "wrong",
                "user_error_reason": "把定义记反了",
                "reason_category": "concept",
                "mistake_reason": "定义记反",
                "knowledge_point_ids": [kp_id],
                "confirmed_candidate": body["candidate"],
            }

            # wrong actor is forbidden
            main.app.dependency_overrides[get_current_admin] = _override(other)
            forbidden = await client.post("/api/admin/mistakes/ai-confirm", json=confirm_body)
            assert forbidden.status_code == 403, forbidden.text

            main.app.dependency_overrides[get_current_admin] = _override(admin)
            created = await client.post("/api/admin/mistakes/ai-confirm", json=confirm_body)
            assert created.status_code == 200, created.text
            draft_id = created.json()["draft_item_id"]
            state.draft_item_ids.append(uuid.UUID(draft_id))

            async with async_session() as session:
                run = await session.get(AiRun, uuid.UUID(run_id))
                assert run.target_type == "MistakeDraft"
                assert run.target_id == draft_id
                assert run.confirmed_payload_hash
                assert run.review_status == "accepted"
                snapshot = run.creation_context["confirmed_snapshot"]
                assert snapshot["payload_hash"] == run.confirmed_payload_hash
                assert snapshot["payload"]["my_answer"] == "wrong"
                assert snapshot["payload"]["user_error_reason"] == "把定义记反了"
                count = await session.scalar(
                    select(func.count())
                    .select_from(MistakeDraft)
                    .where(MistakeDraft.draft_item_id == uuid.UUID(draft_id))
                )
                assert count == 1

            # replay with identical payload returns the original draft, no new one
            replay = await client.post("/api/admin/mistakes/ai-confirm", json=confirm_body)
            assert replay.status_code == 200, replay.text
            assert replay.json()["draft_item_id"] == draft_id

            # different payload conflicts (does not overwrite the target)
            changed = dict(confirm_body)
            changed["my_answer"] = "different"
            conflict = await client.post("/api/admin/mistakes/ai-confirm", json=changed)
            assert conflict.status_code == 409, conflict.text

            # changed source question version conflicts on a fresh unbound run
            with patch(
                "app.services.ai_gateway._call_with_fallback",
                new=AsyncMock(return_value=_fake_call_result()),
            ), patch("app.services.ai_gateway._write_call_log", new=AsyncMock()):
                second = await client.post(
                    "/api/admin/mistakes/ai-candidate",
                    json={
                        "question_id": str(question_id),
                        "my_answer": "wrong",
                        "user_error_reason": "把定义记反了",
                    },
                )
            second_body = second.json()
            state.run_ids.append(uuid.UUID(second_body["run_id"]))

            # A01: an unbound run rejects a confirmation whose input no longer
            # matches the generation input recorded on the run context.
            mismatched_input = dict(confirm_body)
            mismatched_input["run_id"] = second_body["run_id"]
            mismatched_input["review_revision"] = second_body["review_revision"]
            mismatched_input["user_error_reason"] = "换了一个错因说明"
            input_conflict = await client.post(
                "/api/admin/mistakes/ai-confirm", json=mismatched_input
            )
            assert input_conflict.status_code == 409, input_conflict.text

            async with async_session() as session:
                question = await session.get(Question, question_id)
                question.version += 1
                await session.commit()
            stale = dict(confirm_body)
            stale["run_id"] = second_body["run_id"]
            stale["review_revision"] = second_body["review_revision"]
            stale_conflict = await client.post("/api/admin/mistakes/ai-confirm", json=stale)
            assert stale_conflict.status_code == 409, stale_conflict.text
    finally:
        main.app.dependency_overrides.pop(get_current_admin, None)


async def _concurrency_scenario(state: _State) -> None:
    admin = await _seed_admin(state, "conc")
    question_id, _kp = await _seed_question(state, uuid.uuid4().hex[:8])

    async with async_session() as session:
        from app.services.ai_run_service import start_ai_run

        context = ai_creation_service.build_creation_context(
            purpose=ai_creation_service.PURPOSE_CANONICAL_MISTAKE_DRAFT,
            source_question_id=question_id,
            source_question_version=1,
            input_hash="deadbeef",
            output_schema="ErrorInterpretationResponse",
            prompt_version="v1",
        )
        run = await start_ai_run(
            session,
            task_type="mistake_error_interpretation",
            review_required=True,
            creation_context=context,
            created_by=admin.id,
        )
        run.status = "succeeded"
        run.validation_status = "passed"
        await session.commit()
        run_id = run.id
        state.run_ids.append(run_id)

    make_payload = lambda answer: {  # noqa: E731
        "question_id": str(question_id),
        "my_answer": answer,
        "reason_category": "concept",
        "mistake_reason": None,
        "difficulty": None,
        "knowledge_point_ids": [],
        "confirmed_candidate": {},
    }

    async def _confirm(session, payload):
        async def create_entity(run, context):
            record = await mistake_service.create_mistake_draft(
                session,
                __import__("app.schemas.mistake", fromlist=["MistakeDraftCreate"]).MistakeDraftCreate(
                    question_id=question_id,
                    my_answer=payload["my_answer"],
                ),
                created_by=admin.id,
            )
            return str(record.item.id)

        async def load_entity(entity_id):
            try:
                return await mistake_service.get_mistake_draft(session, uuid.UUID(entity_id))
            except Exception:
                return None

        try:
            result = await ai_creation_service.confirm_canonical_creation(
                session,
                run_id=run_id,
                expected_revision=0,
                actor_id=admin.id,
                entity_type="MistakeDraft",
                purpose=ai_creation_service.PURPOSE_CANONICAL_MISTAKE_DRAFT,
                payload=payload,
                create_entity=create_entity,
                load_entity=load_entity,
            )
            await session.commit()
            return result
        except Exception as error:  # noqa: BLE001
            await session.rollback()
            return error

    # identical payload: exactly one creates, the other sees the same entity
    async with async_session() as s1, async_session() as s2:
        r1, r2 = await asyncio.gather(
            _confirm(s1, make_payload("same")),
            _confirm(s2, make_payload("same")),
        )
    outcomes = [r for r in (r1, r2) if not isinstance(r, Exception)]
    assert len(outcomes) == 2, (r1, r2)
    assert len({entity_id for entity_id, _ in outcomes}) == 1
    assert sorted(created for _, created in outcomes) == [False, True]
    state.draft_item_ids.append(uuid.UUID(outcomes[0][0]))

    # different payload: exactly one creates, the other conflicts
    async with async_session() as session:
        from app.services.ai_run_service import start_ai_run

        context = ai_creation_service.build_creation_context(
            purpose=ai_creation_service.PURPOSE_CANONICAL_MISTAKE_DRAFT,
            source_question_id=question_id,
            source_question_version=1,
            input_hash="deadbeef2",
            output_schema="ErrorInterpretationResponse",
            prompt_version="v1",
        )
        run = await start_ai_run(
            session,
            task_type="mistake_error_interpretation",
            review_required=True,
            creation_context=context,
            created_by=admin.id,
        )
        run.status = "succeeded"
        run.validation_status = "passed"
        await session.commit()
        run2_id = run.id
        state.run_ids.append(run2_id)

    async def _confirm2(session, answer):
        async def create_entity(run, context):
            record = await mistake_service.create_mistake_draft(
                session,
                __import__("app.schemas.mistake", fromlist=["MistakeDraftCreate"]).MistakeDraftCreate(
                    question_id=question_id, my_answer=answer
                ),
                created_by=admin.id,
            )
            return str(record.item.id)

        async def load_entity(entity_id):
            try:
                return await mistake_service.get_mistake_draft(session, uuid.UUID(entity_id))
            except Exception:
                return None

        try:
            result = await ai_creation_service.confirm_canonical_creation(
                session,
                run_id=run2_id,
                expected_revision=0,
                actor_id=admin.id,
                entity_type="MistakeDraft",
                purpose=ai_creation_service.PURPOSE_CANONICAL_MISTAKE_DRAFT,
                payload=make_payload(answer),
                create_entity=create_entity,
                load_entity=load_entity,
            )
            await session.commit()
            return result
        except Exception as error:  # noqa: BLE001
            await session.rollback()
            return error

    async with async_session() as s1, async_session() as s2:
        r1, r2 = await asyncio.gather(_confirm2(s1, "x"), _confirm2(s2, "y"))

    created_results = [r for r in (r1, r2) if not isinstance(r, Exception)]
    conflicts = [r for r in (r1, r2) if isinstance(r, Exception)]
    assert len(created_results) == 1, (r1, r2)
    assert len(conflicts) == 1, (r1, r2)
    state.draft_item_ids.append(uuid.UUID(created_results[0][0]))


async def _run() -> None:
    state = _State()
    try:
        await _http_scenario(state)
        await _concurrency_scenario(state)
    finally:
        await _cleanup(state)
        await engine.dispose()


def test_canonical_ai_creation_closure() -> None:
    asyncio.run(_run())
