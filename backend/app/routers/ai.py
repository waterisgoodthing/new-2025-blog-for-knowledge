from fastapi import APIRouter, Cookie, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.routers.auth import get_current_admin
from app.schemas.ai import (
    AnalyzeRequest,
    AnalyzeResponse,
    DiagramResponse,
    DiagramStrategyRequest,
    ErrorInterpretationRequest,
    ErrorInterpretationResponse,
    FinalAnalysisRequest,
    FinalAnalysisResponse,
    InterpretationRejectionRequest,
    QuestionDraftConfirmRequest,
    QuestionDraftConfirmResponse,
    QuestionDraftRequest,
    QuestionDraftResponse,
    TextAnalyzeRequest,
)
from app.schemas.knowledge import (
    InsufficientContextResponse,
    KnowledgeSummaryRequest,
    KnowledgeSummaryResponse,
)
from app.services.audit_service import audit_action
from app.services.ai_gateway import call_text, call_vision
from app.services.ai_prompt_registry import (
    build_text_messages,
    build_vision_messages,
    get_prompt_template,
)
from app.services.ai_task_types import AiTaskType
from app.services.ai_analyze_service import (
    PROMPT_TEMPLATES,
    check_rate_limit,
    build_personal_context,
    build_summary_user_content,
    parse_summary_blocks,
    build_ai_config,
    stream_analyze_events,
    analyze_and_parse,
    build_prompts_response,
)
from app.schemas.ai_call_log import (
    AiCallLogOut,
    AiCallLogStatsResponse,
    AiProviderHealthSnapshotResponse,
    AiUsageCostStatsResponse,
)
from app.services.ai_log_service import (
    query_call_logs,
    query_call_log_stats,
    query_provider_health_snapshot,
    query_usage_cost_stats,
)
from app.services.ai_service import get_provider_status
from app.services.mistake_staged_service import (
    generate_error_interpretation,
    generate_final_analysis,
    generate_question_draft,
)
from app.services.diagram_service import (
    classify_diagram_strategy,
    generate_qwen_image_fallback,
    generate_structured_diagram,
)

router = APIRouter(prefix="/api/ai", tags=["ai"])


@router.get("/config")
async def get_ai_config(
    _admin=Depends(get_current_admin),
):
    return build_ai_config()


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_mistake(
    req: AnalyzeRequest,
    request: Request,
    _admin=Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
    session_token: str | None = Cookie(None, alias="admin_session"),
):
    check_rate_limit()
    if not req.images:
        raise HTTPException(status_code=400, detail="At least one image is required")

    await audit_action(
        db, action="ai_call", session_token=session_token, request=request,
        entity_type="ai_analyze", after={"image_count": len(req.images)},
    )

    content = [{"type": "text", "text": get_prompt_template(AiTaskType.ANALYZE_MISTAKE).user_content_template or ""}]
    for img in req.images:
        content.append({
            "type": "image_url",
            "image_url": {"url": f"data:{img.mime_type};base64,{img.base64}"},
        })

    personal_ctx = build_personal_context(req.my_answer, req.correct_answer, req.user_error_analysis)
    if personal_ctx:
        content.append({"type": "text", "text": personal_ctx})

    messages = build_vision_messages(AiTaskType.ANALYZE_MISTAKE, content)

    try:
        gw = await call_vision(AiTaskType.ANALYZE_MISTAKE, messages)
        result = gw.data
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))

    return await analyze_and_parse(result, db, call_vision)


@router.post("/analyze-text", response_model=AnalyzeResponse)
async def analyze_text(
    req: TextAnalyzeRequest,
    request: Request,
    _admin=Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
    session_token: str | None = Cookie(None, alias="admin_session"),
):
    check_rate_limit()
    if not req.text.strip():
        raise HTTPException(status_code=400, detail="Text is required")

    await audit_action(
        db, action="ai_call", session_token=session_token, request=request,
        entity_type="ai_analyze_text", after={"text_length": len(req.text)},
    )

    user_content = req.text
    personal_ctx = build_personal_context(req.my_answer, req.correct_answer, req.user_error_analysis)
    if personal_ctx:
        user_content += personal_ctx

    messages = build_text_messages(AiTaskType.ANALYZE_TEXT, user_content)

    try:
        gw = await call_text(AiTaskType.ANALYZE_TEXT, messages)
        result = gw.data
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))

    return await analyze_and_parse(result, db, call_text)


@router.post("/analyze-stream", deprecated=True)
async def analyze_mistake_stream(
    req: AnalyzeRequest,
    request: Request,
    _admin=Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
    session_token: str | None = Cookie(None, alias="admin_session"),
):
    check_rate_limit()
    if not req.images:
        raise HTTPException(status_code=400, detail="至少需要一张图片")

    await audit_action(
        db, action="ai_call", session_token=session_token, request=request,
        entity_type="ai_analyze_stream", after={"image_count": len(req.images)},
    )

    content = [{"type": "text", "text": get_prompt_template(AiTaskType.ANALYZE_MISTAKE).user_content_template or ""}]
    for img in req.images:
        content.append({
            "type": "image_url",
            "image_url": {"url": f"data:{img.mime_type};base64,{img.base64}"},
        })

    personal_ctx = build_personal_context(req.my_answer, req.correct_answer, req.user_error_analysis)
    if personal_ctx:
        content.append({"type": "text", "text": personal_ctx})

    messages = [
        {"role": "system", "content": get_prompt_template(AiTaskType.ANALYZE_MISTAKE).system_prompt},
        {"role": "user", "content": content},
    ]

    return StreamingResponse(
        stream_analyze_events(messages, call_vision, AiTaskType.ANALYZE_MISTAKE, db),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive", "X-Accel-Buffering": "no"},
    )


@router.post("/analyze-text-stream", deprecated=True)
async def analyze_text_stream(
    req: TextAnalyzeRequest,
    request: Request,
    _admin=Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
    session_token: str | None = Cookie(None, alias="admin_session"),
):
    check_rate_limit()
    if not req.text.strip():
        raise HTTPException(status_code=400, detail="请输入题目文本")

    await audit_action(
        db, action="ai_call", session_token=session_token, request=request,
        entity_type="ai_analyze_text_stream", after={"text_length": len(req.text)},
    )

    user_content = req.text
    personal_ctx = build_personal_context(req.my_answer, req.correct_answer, req.user_error_analysis)
    if personal_ctx:
        user_content += personal_ctx

    messages = [
        {"role": "system", "content": get_prompt_template(AiTaskType.ANALYZE_TEXT).system_prompt},
        {"role": "user", "content": user_content},
    ]

    return StreamingResponse(
        stream_analyze_events(messages, call_text, AiTaskType.ANALYZE_TEXT, db),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive", "X-Accel-Buffering": "no"},
    )


@router.post("/generate-variant")
async def generate_variant(
    req: dict,
    request: Request,
    _admin=Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
    session_token: str | None = Cookie(None, alias="admin_session"),
):
    check_rate_limit()
    knowledge_point = req.get("knowledge_point", "").strip()
    subject = req.get("subject", "").strip()
    if not knowledge_point:
        raise HTTPException(status_code=400, detail="knowledge_point is required")

    await audit_action(
        db, action="ai_call", session_token=session_token, request=request,
        entity_type="ai_generate_variant", after={"knowledge_point": knowledge_point},
    )

    user_content = f"知识点: {knowledge_point}"
    if subject:
        user_content += f"\n学科: {subject}"

    messages = build_text_messages(AiTaskType.GENERATE_VARIANT, user_content)

    try:
        gw = await call_text(AiTaskType.GENERATE_VARIANT, messages)
        result = gw.data
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))

    return {
        "question": result.get("question", ""),
        "correct_answer": result.get("correct_answer", ""),
        "analysis": result.get("analysis", ""),
        "difficulty": result.get("difficulty", "medium"),
        "knowledge_points": result.get("knowledge_points", knowledge_point),
        "subject": subject,
    }


@router.post("/generate-knowledge-card")
async def generate_knowledge_card(
    req: dict,
    request: Request,
    _admin=Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
    session_token: str | None = Cookie(None, alias="admin_session"),
):
    check_rate_limit()
    knowledge_point = req.get("knowledge_point", "").strip()
    subject = req.get("subject", "").strip()
    if not knowledge_point:
        raise HTTPException(status_code=400, detail="knowledge_point is required")

    await audit_action(
        db, action="ai_call", session_token=session_token, request=request,
        entity_type="ai_generate_knowledge_card", after={"knowledge_point": knowledge_point},
    )

    user_content = f"知识点: {knowledge_point}"
    if subject:
        user_content += f"\n学科: {subject}"

    messages = build_text_messages(AiTaskType.GENERATE_KNOWLEDGE_CARD, user_content)

    try:
        gw = await call_text(AiTaskType.GENERATE_KNOWLEDGE_CARD, messages)
        result = gw.data
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))

    return {
        "title": result.get("title", knowledge_point),
        "content": result.get("content", ""),
        "knowledge_points": result.get("knowledge_points", knowledge_point),
        "subject": result.get("subject", subject),
    }


@router.post("/knowledge-summary", response_model=KnowledgeSummaryResponse | InsufficientContextResponse)
async def knowledge_summary(
    request_body: KnowledgeSummaryRequest,
    request: Request,
    _admin=Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
    session_token: str | None = Cookie(None, alias="admin_session"),
):
    check_rate_limit()

    await audit_action(
        db, action="ai_call", session_token=session_token, request=request,
        entity_type="ai_knowledge_summary", after={"source_count": len(request_body.context_pack.sources)},
    )

    sources = request_body.context_pack.sources
    if not sources:
        return InsufficientContextResponse(
            status="insufficient_context",
            message="No usable source references are available for factual generation.",
            outline=[],
        )

    user_content = build_summary_user_content(request_body)
    messages = build_text_messages(AiTaskType.KNOWLEDGE_SUMMARY, user_content)

    try:
        gw = await call_text(AiTaskType.KNOWLEDGE_SUMMARY, messages)
        result = gw.data
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))

    if result.get("status") == "insufficient_context":
        return InsufficientContextResponse(
            status="insufficient_context",
            message=result.get("message", "No usable source references are available for factual generation."),
            outline=result.get("outline", []),
        )

    blocks = parse_summary_blocks(result, sources)
    return KnowledgeSummaryResponse(
        title=result.get("title", ""),
        blocks=blocks,
    )


@router.get("/prompts")
async def get_prompts(
    _admin=Depends(get_current_admin),
):
    return build_prompts_response()


@router.post("/prompt-test")
async def prompt_test(
    req: dict,
    _admin=Depends(get_current_admin),
):
    prompt_key = req.get("prompt_key", "")
    sample_input = req.get("sample_input", "")
    custom_prompt = req.get("custom_prompt", "")
    route = req.get("route", "text JSON")

    if not sample_input:
        raise HTTPException(status_code=400, detail="sample_input is required")

    system_prompt = custom_prompt
    if not system_prompt and prompt_key:
        group, _, key = prompt_key.partition(".")
        tmpl = PROMPT_TEMPLATES.get(group, {}).get(key, {})
        system_prompt = tmpl.get("full_prompt") or tmpl.get("prompt", "")
    if not system_prompt:
        raise HTTPException(status_code=400, detail="No prompt found")

    messages = build_text_messages(AiTaskType.PROMPT_TEST, sample_input, system_prompt_override=system_prompt)

    is_json = "json" in route.lower()
    try:
        if "text" in route.lower():
            gw = await call_text(AiTaskType.PROMPT_TEST, messages, max_tokens=2000, json_mode=is_json, preferred="deepseek")
        else:
            gw = await call_vision(AiTaskType.PROMPT_TEST, messages, max_tokens=2000)
        return {"success": gw.success, "provider_used": gw.provider_used, "fallback_used": gw.fallback_used, "latency_ms": gw.latency_ms, "output": gw.data, "attempts": gw.attempts, "error": gw.error}
    except Exception as e:
        return {"success": False, "provider_used": "", "fallback_used": False, "latency_ms": 0, "output": None, "error": str(e)[:300], "attempts": []}


@router.get("/provider-status")
async def provider_status(
    _admin=Depends(get_current_admin),
):
    return await get_provider_status()


@router.get("/provider-health-snapshot", response_model=AiProviderHealthSnapshotResponse)
async def provider_health_snapshot(
    _admin=Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    items = await query_provider_health_snapshot(db)
    return AiProviderHealthSnapshotResponse(items=items)


@router.get("/call-logs", response_model=list[AiCallLogOut])
async def list_call_logs(
    task_type: str | None = None,
    success: bool | None = None,
    provider: str | None = None,
    limit: int = 20,
    offset: int = 0,
    _admin=Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    limit = min(max(limit, 1), 100)
    logs = await query_call_logs(db, task_type=task_type, success=success, provider=provider, limit=limit, offset=offset)
    return logs


@router.get("/call-logs/stats", response_model=AiCallLogStatsResponse)
async def call_log_stats(
    _admin=Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    items = await query_call_log_stats(db)
    return AiCallLogStatsResponse(items=items)


@router.get("/call-logs/usage-cost", response_model=AiUsageCostStatsResponse)
async def call_log_usage_cost_stats(
    _admin=Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    items = await query_usage_cost_stats(db)
    return AiUsageCostStatsResponse(items=items)


# --- Staged mistake workflow endpoints ---


@router.post("/mistake/question-draft", response_model=QuestionDraftResponse)
async def mistake_question_draft(
    req: QuestionDraftRequest,
    request: Request,
    _admin=Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
    session_token: str | None = Cookie(None, alias="admin_session"),
):
    check_rate_limit()
    if not req.images and not req.text.strip():
        raise HTTPException(status_code=400, detail="At least one image or text is required")

    await audit_action(
        db, action="ai_call", session_token=session_token, request=request,
        entity_type="ai_mistake_question_draft", after={"image_count": len(req.images), "has_text": bool(req.text.strip())},
    )

    try:
        result = await generate_question_draft(
            images=[img.model_dump() for img in req.images],
            text=req.text,
        )
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=502, detail=str(e))

    return QuestionDraftResponse(**result)


@router.post("/mistake/question-draft/confirm", response_model=QuestionDraftConfirmResponse)
async def mistake_question_draft_confirm(
    req: QuestionDraftConfirmRequest,
    _admin=Depends(get_current_admin),
):
    now = __import__("datetime").datetime.utcnow().isoformat() + "Z"
    return QuestionDraftConfirmResponse(
        status="confirmed",
        draft=req.draft,
        confirmed_at=now,
    )


@router.post("/mistake/error-interpretation", response_model=ErrorInterpretationResponse)
async def mistake_error_interpretation(
    req: ErrorInterpretationRequest,
    request: Request,
    _admin=Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
    session_token: str | None = Cookie(None, alias="admin_session"),
):
    check_rate_limit()
    if not req.user_error_reason.strip():
        raise HTTPException(status_code=400, detail="user_error_reason is required")

    await audit_action(
        db, action="ai_call", session_token=session_token, request=request,
        entity_type="ai_mistake_error_interpretation", after={"reason_length": len(req.user_error_reason)},
    )

    try:
        result = await generate_error_interpretation(
            question_draft=req.question_draft.model_dump(),
            user_error_reason=req.user_error_reason,
            rejection_history=req.rejection_history,
        )
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=502, detail=str(e))

    return ErrorInterpretationResponse(**result)


@router.post("/mistake/error-interpretation/reject", response_model=ErrorInterpretationResponse)
async def mistake_error_interpretation_reject(
    req: InterpretationRejectionRequest,
    request: Request,
    _admin=Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
    session_token: str | None = Cookie(None, alias="admin_session"),
):
    check_rate_limit()
    if not req.rejection_reason.strip():
        raise HTTPException(status_code=400, detail="rejection_reason is required")

    await audit_action(
        db, action="ai_call", session_token=session_token, request=request,
        entity_type="ai_mistake_interpretation_reject", after={"rejection_reason": req.rejection_reason[:100]},
    )

    updated_history = list(req.rejection_history) + [req.rejection_reason]

    try:
        result = await generate_error_interpretation(
            question_draft=req.question_draft.model_dump(),
            user_error_reason=req.user_error_reason,
            rejection_history=updated_history,
        )
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=502, detail=str(e))

    return ErrorInterpretationResponse(**result)


@router.post("/mistake/final-analysis", response_model=FinalAnalysisResponse)
async def mistake_final_analysis(
    req: FinalAnalysisRequest,
    request: Request,
    _admin=Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
    session_token: str | None = Cookie(None, alias="admin_session"),
):
    check_rate_limit()

    await audit_action(
        db, action="ai_call", session_token=session_token, request=request,
        entity_type="ai_mistake_final_analysis",
        after={"interpretation_id": req.accepted_interpretation.interpretation_id},
    )

    try:
        result = await generate_final_analysis(
            question_draft=req.question_draft.model_dump(),
            user_error_reason=req.user_error_reason,
            accepted_interpretation=req.accepted_interpretation.model_dump(),
        )
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=502, detail=str(e))

    return FinalAnalysisResponse(**result)


@router.post("/mistake/diagram", response_model=DiagramResponse)
async def mistake_diagram(
    req: DiagramStrategyRequest,
    request: Request,
    _admin=Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
    session_token: str | None = Cookie(None, alias="admin_session"),
):
    check_rate_limit()

    await audit_action(
        db, action="ai_call", session_token=session_token, request=request,
        entity_type="ai_mistake_diagram",
        after={"interpretation_id": req.accepted_interpretation.interpretation_id},
    )

    strategy, reason = classify_diagram_strategy(req.question_draft.model_dump())

    if strategy == "structured":
        structured_data = await generate_structured_diagram(
            question_draft=req.question_draft.model_dump(),
            accepted_interpretation=req.accepted_interpretation.model_dump(),
            final_analysis=req.final_analysis.model_dump(),
        )
        return DiagramResponse(
            strategy="structured",
            strategy_reason=reason,
            structured_data=structured_data,
            accepted_interpretation_id=req.accepted_interpretation.interpretation_id,
            accepted_interpretation_version=req.accepted_interpretation.version,
            uses_error_interpretation=True,
        )

    image_url, image_prompt = await generate_qwen_image_fallback(
        question_draft=req.question_draft.model_dump(),
        accepted_interpretation=req.accepted_interpretation.model_dump(),
        final_analysis=req.final_analysis.model_dump(),
    )
    return DiagramResponse(
        strategy="qwen_image_fallback",
        strategy_reason=reason,
        image_url=image_url,
        image_prompt=image_prompt,
        accepted_interpretation_id=req.accepted_interpretation.interpretation_id,
        accepted_interpretation_version=req.accepted_interpretation.version,
        uses_error_interpretation=True,
    )
