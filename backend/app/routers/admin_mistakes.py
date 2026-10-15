import json
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.note import User
from app.models.question import Question
from app.routers.auth import get_current_admin
from app.schemas.mistake import (
    MistakeAiCandidateRequest,
    MistakeAiCandidateResponse,
    MistakeAiConfirmRequest,
    MistakeDraftCreate,
    MistakeDraftOut,
    MistakeOut,
    MistakeUpdate,
    MistakeVisibilityUpdate,
    VersionCommand,
)
from app.services import ai_creation_service, mistake_service
from app.services.ai_gateway import call_text
from app.services.ai_prompt_registry import build_text_messages, get_prompt_template
from app.services.ai_run_service import (
    AiRunConflict,
    AiRunError,
    AiRunNotFound,
    get_ai_run,
)
from app.services.ai_task_types import AiTaskType

router = APIRouter(
    prefix="/api/admin/mistakes",
    tags=["admin-mistakes"],
    dependencies=[Depends(get_current_admin)],
)


def _raise_http(error: mistake_service.MistakeError) -> None:
    if isinstance(error, mistake_service.MistakeNotFound):
        raise HTTPException(status_code=404, detail=str(error)) from error
    if isinstance(error, mistake_service.MistakeConflict):
        raise HTTPException(status_code=409, detail=str(error)) from error
    raise HTTPException(status_code=400, detail=str(error)) from error


def _raise_ai_http(error: AiRunError) -> None:
    if isinstance(error, AiRunNotFound):
        raise HTTPException(status_code=404, detail=str(error)) from error
    if isinstance(error, ai_creation_service.AiRunForbidden):
        raise HTTPException(status_code=403, detail=str(error)) from error
    if isinstance(error, AiRunConflict):
        raise HTTPException(status_code=409, detail=str(error)) from error
    raise HTTPException(status_code=400, detail=str(error)) from error


@router.get("", response_model=list[MistakeOut])
async def list_mistakes(
    status_filter: str | None = Query(default=None, alias="status"),
    db: AsyncSession = Depends(get_db),
):
    return await mistake_service.list_mistakes(db, status=status_filter)


@router.get("/{mistake_id}", response_model=MistakeOut)
async def get_mistake(
    mistake_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    try:
        return await mistake_service.get_mistake(db, mistake_id)
    except mistake_service.MistakeError as error:
        _raise_http(error)


@router.put("/{mistake_id}", response_model=MistakeOut)
async def update_mistake(
    mistake_id: uuid.UUID,
    payload: MistakeUpdate,
    db: AsyncSession = Depends(get_db),
):
    try:
        return await mistake_service.update_mistake(db, mistake_id, payload)
    except mistake_service.MistakeError as error:
        _raise_http(error)


@router.patch("/{mistake_id}/visibility", response_model=MistakeOut)
async def update_mistake_visibility(
    mistake_id: uuid.UUID,
    payload: MistakeVisibilityUpdate,
    db: AsyncSession = Depends(get_db),
):
    try:
        return await mistake_service.update_mistake_visibility(
            db,
            mistake_id,
            visibility=payload.visibility,
            version=payload.version,
        )
    except mistake_service.MistakeError as error:
        _raise_http(error)


@router.delete("/{mistake_id}", response_model=MistakeOut)
async def archive_mistake(
    mistake_id: uuid.UUID,
    payload: VersionCommand,
    db: AsyncSession = Depends(get_db),
):
    try:
        return await mistake_service.archive_mistake(
            db,
            mistake_id,
            version=payload.version,
        )
    except mistake_service.MistakeError as error:
        _raise_http(error)


def _interpretation_user_content(
    question: Question,
    my_answer: str | None,
    user_error_reason: str,
) -> str:
    answer_value = (question.answer_data or {}).get("value") or question.correct_answer
    return (
        f"题目信息：\n{question.stem_md or question.question_text}\n\n"
        f"正确答案：{answer_value}\n\n"
        f"学生本次作答：{my_answer or ''}\n\n"
        f"学生自述错因：{user_error_reason}"
    )


@router.post("/ai-candidate", response_model=MistakeAiCandidateResponse)
async def create_ai_candidate(
    payload: MistakeAiCandidateRequest,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    """Generate a trusted AI error-interpretation candidate for a formal question.

    B05b: the server builds and persists the immutable creation context (source
    question id + version, normalized input hash, output schema, prompt version)
    on the AiRun *before* the provider call. The returned ``run_id`` and
    ``review_revision`` are the only accepted handles for a later confirmation.
    """
    question = await db.get(Question, payload.question_id)
    if question is None or question.status != "active":
        raise HTTPException(status_code=404, detail="Active question not found")
    if not (payload.user_error_reason or "").strip():
        raise HTTPException(status_code=400, detail="user_error_reason is required")

    template = get_prompt_template(AiTaskType.MISTAKE_ERROR_INTERPRETATION)
    context = ai_creation_service.build_creation_context(
        purpose=ai_creation_service.PURPOSE_CANONICAL_MISTAKE_DRAFT,
        source_question_id=question.id,
        source_question_version=question.version,
        input_hash=ai_creation_service.canonical_input_hash(
            question_id=question.id,
            question_version=question.version,
            my_answer=payload.my_answer,
            user_error_reason=payload.user_error_reason,
        ),
        output_schema="ErrorInterpretationResponse",
        prompt_version=template.version,
        input_summary=payload.user_error_reason,
    )

    messages = build_text_messages(
        AiTaskType.MISTAKE_ERROR_INTERPRETATION,
        _interpretation_user_content(question, payload.my_answer, payload.user_error_reason),
    )
    gw = await call_text(
        AiTaskType.MISTAKE_ERROR_INTERPRETATION,
        messages,
        input_summary=(payload.user_error_reason or "")[:200],
        creation_context=context,
        created_by=admin.id,
    )
    if not gw.success or gw.run_id is None:
        raise HTTPException(status_code=502, detail="AI 服务暂时不可用，请稍后重试")

    run = await get_ai_run(db, gw.run_id)
    return MistakeAiCandidateResponse(
        run_id=run.id,
        review_revision=run.review_revision,
        candidate=gw.data if isinstance(gw.data, dict) else {},
    )


@router.post("/ai-confirm", response_model=MistakeDraftOut)
async def confirm_ai_candidate(
    payload: MistakeAiConfirmRequest,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    """Confirm a trusted AI run into a canonical MistakeDraft, atomically.

    Row-locks the run, verifies actor/purpose/status/validation/revision (and,
    for a first confirmation, the live source question version), then creates
    the draft and binds the run in one transaction. Replaying the identical
    payload returns the original draft; a different payload conflicts.
    """
    confirmed_candidate = payload.confirmed_candidate or {}
    confirmed_payload = {
        "question_id": str(payload.question_id),
        "my_answer": (payload.my_answer or "").strip() or None,
        "user_error_reason": (payload.user_error_reason or "").strip() or None,
        "reason_category": payload.reason_category,
        "mistake_reason": (payload.mistake_reason or "").strip() or None,
        "difficulty": payload.difficulty,
        "knowledge_point_ids": sorted(int(value) for value in payload.knowledge_point_ids),
        "confirmed_candidate": confirmed_candidate,
    }

    async def create_entity(run, context) -> str:
        if str(payload.question_id) != context.get("source_question_id"):
            raise AiRunConflict("Confirmed question does not match the AI Run source")
        question = await db.get(Question, payload.question_id)
        if question is None or question.status != "active":
            raise AiRunConflict("Source question is no longer active")
        if int(question.version) != int(context.get("source_question_version") or -1):
            raise AiRunConflict("Source question changed since the AI Run was created")
        expected_input_hash = ai_creation_service.canonical_input_hash(
            question_id=question.id,
            question_version=question.version,
            my_answer=payload.my_answer,
            user_error_reason=payload.user_error_reason,
        )
        if expected_input_hash != context.get("input_hash"):
            raise AiRunConflict("Confirmed input does not match the AI Run source")
        record = await mistake_service.create_mistake_draft(
            db,
            MistakeDraftCreate(
                question_id=payload.question_id,
                my_answer=payload.my_answer,
                reason_category=payload.reason_category,
                mistake_reason=payload.mistake_reason,
                difficulty=payload.difficulty,
                knowledge_point_ids=list(payload.knowledge_point_ids),
            ),
            created_by=admin.id,
        )
        return str(record.item.id)

    async def load_entity(entity_id: str):
        try:
            return await mistake_service.get_mistake_draft(db, uuid.UUID(entity_id))
        except (ValueError, mistake_service.MistakeError):
            return None

    try:
        entity_id, _created = await ai_creation_service.confirm_canonical_creation(
            db,
            run_id=payload.run_id,
            expected_revision=payload.review_revision,
            actor_id=admin.id,
            entity_type=ai_creation_service.CANONICAL_ENTITY_TYPE_MISTAKE_DRAFT,
            purpose=ai_creation_service.PURPOSE_CANONICAL_MISTAKE_DRAFT,
            payload=confirmed_payload,
            create_entity=create_entity,
            load_entity=load_entity,
        )
    except AiRunError as error:
        _raise_ai_http(error)
    return await mistake_service.get_mistake_draft(db, uuid.UUID(entity_id))
