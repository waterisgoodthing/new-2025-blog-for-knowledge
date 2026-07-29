"""Capture service — Batch 8 图片错题采集业务逻辑。

职责：
- 管理 capture_item 生命周期（uploaded → recognizing → recognized → drafting → ready → converted）
- 调用 OCR/AI 窄 adapter（capture_recognition / capture_ai_draft），不直接调用 ai_service
- 显式、幂等、事务化的 capture → mistake_draft 转换

不创建正式 mistake 或 review_item。
转换后人工仍需在 mistake_draft 链路确认，才能进入正式 mistake。
"""

import logging
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.capture import CaptureItem
from app.models.note import Subject
from app.schemas.attachment import AttachmentLinkCreate
from app.schemas.capture import (
    CaptureConvert,
    CaptureCreate,
    CaptureDraftInput,
    CapturePatch,
)
from app.schemas.mistake import MistakeDraftCreate
from app.schemas.question import QuestionDraftCreate
from app.services.attachment_service import (
    AttachmentConflict,
    AttachmentNotFound,
    create_attachment_link,
    get_attachment,
    get_attachment_content_path,
)
from app.services.capture_ai_draft import draft_mistake
from app.services.capture_recognition import recognize_image
from app.services.draft_service import create_question_draft
from app.services.mistake_service import create_mistake_draft, get_mistake_draft

logger = logging.getLogger(__name__)


class CaptureError(Exception):
    pass


class CaptureNotFound(CaptureError):
    pass


class CaptureConflict(CaptureError):
    pass


class CaptureValidationError(CaptureError):
    pass


_PATCHABLE_STATUSES = {"uploaded", "recognized", "ready", "failed"}


@dataclass
class ConvertResult:
    """转换结果。"""

    capture: CaptureItem
    mistake_draft_item_id: uuid.UUID
    question_draft_id: uuid.UUID | None


async def create_capture(
    session: AsyncSession,
    payload: CaptureCreate,
    *,
    created_by: uuid.UUID | None = None,
) -> CaptureItem:
    """从已上传 attachment 创建 capture_item。"""
    attachment = await get_attachment(session, payload.attachment_id)
    if attachment.status != "active":
        raise CaptureConflict("Attachment is not active")
    if not attachment.mime_type.startswith("image/"):
        raise CaptureValidationError("Attachment must be an image")

    capture = CaptureItem(
        source_attachment_id=attachment.id,
        status="uploaded",
        created_by=created_by,
    )
    session.add(capture)
    await session.flush()
    await session.refresh(capture)
    return capture


async def get_capture(
    session: AsyncSession,
    capture_id: uuid.UUID,
    *,
    for_update: bool = False,
) -> CaptureItem:
    statement = select(CaptureItem).where(CaptureItem.id == capture_id)
    if for_update:
        statement = statement.with_for_update()
    capture = (await session.execute(statement)).scalar_one_or_none()
    if capture is None:
        raise CaptureNotFound("Capture item not found")
    return capture


async def list_captures(
    session: AsyncSession,
    *,
    status: str | None = None,
) -> list[CaptureItem]:
    statement = select(CaptureItem)
    if status is not None:
        statement = statement.where(CaptureItem.status == status)
    result = await session.execute(statement.order_by(CaptureItem.created_at.desc()))
    return list(result.scalars().all())


async def patch_capture(
    session: AsyncSession,
    capture_id: uuid.UUID,
    payload: CapturePatch,
) -> CaptureItem:
    """人工编辑 capture 草稿字段。

    所有 AI 生成内容均可人工覆盖或清空。
    如果人工提供了 question_draft_text，自动进入 ready 状态（无需 AI）。
    如果当前为 failed 状态，编辑后自动回到 ready。
    """
    capture = await get_capture(session, capture_id, for_update=True)
    if capture.status not in _PATCHABLE_STATUSES:
        raise CaptureConflict(f"Cannot edit a {capture.status} capture")

    changes = payload.model_dump(exclude_unset=True)

    if "recognized_text" in changes:
        capture.recognized_text = changes["recognized_text"]
    if "user_error_context" in changes:
        capture.user_error_context = changes["user_error_context"]
    if "question_draft_text" in changes:
        capture.question_draft_text = changes["question_draft_text"]
    if "analysis_draft_text" in changes:
        capture.analysis_draft_text = changes["analysis_draft_text"]
    if "error_summary_draft" in changes:
        capture.error_summary_draft = changes["error_summary_draft"]
    if "subject_id" in changes:
        capture.subject_id = changes["subject_id"]
    if "knowledge_point_suggestions" in changes:
        capture.knowledge_point_suggestions = changes["knowledge_point_suggestions"]

    # 失败状态编辑后回到 ready（人工修正）
    if capture.status == "failed":
        capture.status = "ready"
        capture.error_code = None
        capture.error_message_safe = None

    # 人工提供题面草稿即进入 ready（跳过 AI 路径）
    if capture.question_draft_text and capture.status in ("uploaded", "recognized"):
        capture.status = "ready"

    await session.flush()
    await session.refresh(capture)
    return capture


async def trigger_recognition(
    session: AsyncSession,
    capture_id: uuid.UUID,
    *,
    use_fake: bool = False,
    fake_text: str = "",
) -> CaptureItem:
    """触发 OCR/多模态识别。

    失败时只写 capture_items 错误字段，不抛异常，不污染下游。
    """
    capture = await get_capture(session, capture_id, for_update=True)
    if capture.status in ("converted", "archived"):
        raise CaptureConflict(f"Cannot recognize a {capture.status} capture")

    capture.status = "recognizing"
    capture.started_at = datetime.now(timezone.utc)
    capture.last_stage = "recognize"
    capture.attempt_count += 1
    capture.error_code = None
    capture.error_message_safe = None
    await session.flush()

    # 读取附件内容
    try:
        path = await get_attachment_content_path(
            session, capture.source_attachment_id
        )
        image_bytes = path.read_bytes()
    except AttachmentNotFound:
        capture.status = "failed"
        capture.error_code = "attachment_missing"
        capture.error_message_safe = "Source attachment not found"
        capture.finished_at = datetime.now(timezone.utc)
        await session.flush()
        await session.refresh(capture)
        return capture

    attachment = await get_attachment(session, capture.source_attachment_id)

    result = await recognize_image(
        image_bytes,
        attachment.mime_type,
        use_fake=use_fake,
        fake_text=fake_text,
    )

    if result.success:
        capture.recognized_text = result.recognized_text
        capture.status = "recognized"
    else:
        capture.status = "failed"
        capture.error_code = result.error_code
        capture.error_message_safe = result.error_message_safe

    capture.finished_at = datetime.now(timezone.utc)
    await session.flush()
    await session.refresh(capture)
    return capture


async def trigger_draft(
    session: AsyncSession,
    capture_id: uuid.UUID,
    *,
    use_fake: bool = False,
) -> CaptureItem:
    """触发 AI 草稿生成。

    失败时只写 capture_items 错误字段，不抛异常，不污染下游。
    """
    capture = await get_capture(session, capture_id, for_update=True)
    if capture.status in ("converted", "archived"):
        raise CaptureConflict(f"Cannot draft a {capture.status} capture")
    if capture.status not in ("recognized", "failed", "ready"):
        raise CaptureConflict(
            f"Capture must be recognized first (current: {capture.status})"
        )

    if not capture.recognized_text:
        capture.status = "failed"
        capture.error_code = "empty_input"
        capture.error_message_safe = "Recognized text is empty"
        capture.last_stage = "draft"
        capture.started_at = datetime.now(timezone.utc)
        capture.finished_at = datetime.now(timezone.utc)
        await session.flush()
        await session.refresh(capture)
        return capture

    capture.status = "drafting"
    capture.started_at = datetime.now(timezone.utc)
    capture.last_stage = "draft"
    capture.attempt_count += 1
    capture.error_code = None
    capture.error_message_safe = None
    await session.flush()

    # 获取学科标签（用于 AI 上下文）
    subject_label = None
    if capture.subject_id is not None:
        subject = await session.get(Subject, capture.subject_id)
        if subject:
            subject_label = subject.name

    draft_input = CaptureDraftInput(
        recognized_text=capture.recognized_text,
        user_error_context=capture.user_error_context,
        subject_id=capture.subject_id,
        subject_label=subject_label,
    )

    result = await draft_mistake(draft_input, use_fake=use_fake)

    if result.success and result.suggestion:
        capture.question_draft_text = result.suggestion.question_text
        capture.analysis_draft_text = result.suggestion.analysis_text
        capture.error_summary_draft = result.suggestion.error_summary
        capture.knowledge_point_suggestions = [
            kp.model_dump() for kp in result.suggestion.knowledge_point_suggestions
        ]
        capture.status = "ready"
    else:
        capture.status = "failed"
        capture.error_code = result.error_code
        capture.error_message_safe = result.error_message_safe

    capture.finished_at = datetime.now(timezone.utc)
    await session.flush()
    await session.refresh(capture)
    return capture


async def convert_capture(
    session: AsyncSession,
    capture_id: uuid.UUID,
    payload: CaptureConvert,
    *,
    created_by: uuid.UUID | None = None,
) -> ConvertResult:
    """显式、幂等、事务化的 capture → mistake_draft 转换。

    转换流程：
    1. 校验 capture 为 ready 状态（已 converted 返回幂等结果）
    2. 创建 QuestionDraft（从人工确认的题面信息）
    3. 创建 MistakeDraft（从 question_draft）
    4. 关联原图到 question_draft（target_type='question_draft', purpose='source'）
    5. 标记 capture 为 converted，保存 mistake_draft_item_id

    不创建正式 mistake 或 review_item。
    人工仍需在 mistake_draft 链路确认后，才能通过 convert_mistake_draft 进入正式 mistake。
    事务由 get_db 依赖管理，任何步骤失败自动回滚，不留半成品。
    """
    capture = await get_capture(session, capture_id, for_update=True)

    # 幂等：已转换则返回既有结果
    if capture.status == "converted":
        if capture.mistake_draft_item_id is None:
            raise CaptureConflict("Converted capture has no mistake draft")
        mistake_record = await get_mistake_draft(
            session, capture.mistake_draft_item_id
        )
        return ConvertResult(
            capture=capture,
            mistake_draft_item_id=capture.mistake_draft_item_id,
            question_draft_id=mistake_record.question_draft_id,
        )

    if capture.status == "archived":
        raise CaptureConflict("Cannot convert an archived capture")
    if capture.status != "ready":
        raise CaptureConflict(
            f"Capture must be ready to convert (current: {capture.status})"
        )

    # 1. 创建 QuestionDraft（从人工确认的题面信息）
    question_draft_payload = QuestionDraftCreate(
        subject_id=payload.subject_id,
        title=None,
        question_text=payload.question_text,
        question_type=payload.question_type,
        options=payload.options,
        correct_answer=payload.correct_answer,
        explanation=payload.explanation,
        difficulty=payload.difficulty,
        knowledge_point_ids=payload.knowledge_point_ids,
    )
    question_draft_record = await create_question_draft(
        session, question_draft_payload, created_by=created_by
    )

    # 2. 创建 MistakeDraft（从 question_draft）
    mistake_draft_payload = MistakeDraftCreate(
        question_draft_id=question_draft_record.draft.id,
        my_answer=payload.my_answer,
        reason_category=payload.reason_category,
        mistake_reason=payload.mistake_reason,
        difficulty=payload.difficulty,
        knowledge_point_ids=payload.knowledge_point_ids,
    )
    mistake_draft_record = await create_mistake_draft(
        session, mistake_draft_payload, created_by=created_by
    )

    # 3. 关联原图到 question_draft
    try:
        await create_attachment_link(
            session,
            AttachmentLinkCreate(
                attachment_id=capture.source_attachment_id,
                target_type="question_draft",
                target_id=question_draft_record.draft.id,
                purpose="source",
            ),
        )
    except AttachmentConflict:
        logger.warning(
            "Attachment link already exists for capture %s -> question_draft %s",
            capture_id,
            question_draft_record.draft.id,
        )

    # 4. 标记 capture 为 converted
    capture.status = "converted"
    capture.mistake_draft_item_id = mistake_draft_record.item.id
    capture.last_stage = "convert"
    capture.finished_at = datetime.now(timezone.utc)
    await session.flush()
    await session.refresh(capture)

    return ConvertResult(
        capture=capture,
        mistake_draft_item_id=mistake_draft_record.item.id,
        question_draft_id=question_draft_record.draft.id,
    )
