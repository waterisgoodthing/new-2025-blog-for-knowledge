import uuid
from dataclasses import dataclass
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.mistake import Mistake, MistakeDraft
from app.models.question import DraftItem, Question, QuestionDraft
from app.models.review_item import ReviewItem
from app.models.taxonomy import KnowledgePoint, KnowledgePointLink
from app.schemas.mistake import MistakeDraftCreate, MistakeDraftUpdate, MistakeUpdate

class MistakeError(Exception): pass
class MistakeNotFound(MistakeError): pass
class MistakeConflict(MistakeError): pass
class MistakeValidationError(MistakeError): pass

@dataclass
class MistakeDraftRecord:
    item: DraftItem
    draft: MistakeDraft
    knowledge_point_ids: list[int]

    @property
    def status(self):
        return self.item.status

    @property
    def version(self):
        return self.item.version

    @property
    def target_id(self):
        return self.item.target_id

    def __getattr__(self, name):
        return getattr(self.draft, name)

@dataclass
class MistakeRecord:
    mistake: Mistake
    knowledge_point_ids: list[int]
    review_item_id: uuid.UUID
    def __getattr__(self, name):
        return getattr(self.mistake, name)

async def _links(session, kind, target):
    return list((await session.execute(select(KnowledgePointLink.knowledge_point_id).where(
        KnowledgePointLink.target_type==kind, KnowledgePointLink.target_id==str(target)
    ).order_by(KnowledgePointLink.knowledge_point_id))).scalars().all())

async def _validate_points(session, subject_id, ids):
    if not ids: return
    points=list((await session.execute(select(KnowledgePoint).where(KnowledgePoint.id.in_(ids)))).scalars().all())
    if len(points)!=len(ids): raise MistakeNotFound("Knowledge point not found")
    if any(p.subject_id!=subject_id for p in points): raise MistakeValidationError("Knowledge point subject mismatch")

async def create_mistake_draft(session: AsyncSession, payload: MistakeDraftCreate, created_by=None):
    question=None; qdraft=None
    if payload.question_id: question=await session.get(Question,payload.question_id)
    else: qdraft=await session.get(QuestionDraft,payload.question_draft_id)
    source=question or qdraft
    if source is None: raise MistakeNotFound("Question source not found")
    await _validate_points(session,source.subject_id,payload.knowledge_point_ids)
    item=DraftItem(draft_type="mistake",source_type="question" if question else "question_draft",
                   source_id=str(source.id),status="pending",created_by=created_by)
    session.add(item); await session.flush()
    draft=MistakeDraft(draft_item_id=item.id,question_id=question.id if question else None,
        question_draft_id=qdraft.id if qdraft else None,subject_id=source.subject_id,title=source.title,
        question_text=source.question_text,my_answer=payload.my_answer,
        correct_answer_snapshot=source.correct_answer,explanation_snapshot=source.explanation,
        reason_category=payload.reason_category,mistake_reason=payload.mistake_reason,
        difficulty=payload.difficulty or source.difficulty)
    session.add(draft); await session.flush()
    for kp in payload.knowledge_point_ids:
        session.add(KnowledgePointLink(knowledge_point_id=kp,target_type="mistake_draft",target_id=str(draft.id)))
    await session.flush(); await session.refresh(item); await session.refresh(draft)
    return MistakeDraftRecord(item,draft,sorted(payload.knowledge_point_ids))

async def get_mistake_draft(session, item_id, for_update=False):
    stmt=select(DraftItem).where(DraftItem.id==item_id)
    if for_update: stmt=stmt.with_for_update()
    item=(await session.execute(stmt)).scalar_one_or_none()
    if not item or item.draft_type!="mistake": raise MistakeNotFound("Mistake draft not found")
    draft=(await session.execute(select(MistakeDraft).where(MistakeDraft.draft_item_id==item.id))).scalar_one()
    return MistakeDraftRecord(item,draft,await _links(session,"mistake_draft",draft.id))

async def list_mistake_drafts(session):
    items=(await session.execute(select(DraftItem).where(DraftItem.draft_type=="mistake").order_by(DraftItem.updated_at.desc()))).scalars().all()
    return [await get_mistake_draft(session,x.id) for x in items]

async def update_mistake_draft(session,item_id,payload:MistakeDraftUpdate):
    r=await get_mistake_draft(session,item_id,True)
    if r.item.status not in ("pending","needs_fix"): raise MistakeConflict("Draft is not editable")
    if r.item.version!=payload.version: raise MistakeConflict("Draft version conflict")
    changes=payload.model_dump(exclude={"version","knowledge_point_ids"},exclude_unset=True)
    for key, value in changes.items():
        if isinstance(value, str):
            value = value.strip() or None
        setattr(r.draft, key, value)
    if payload.knowledge_point_ids is not None:
        await _validate_points(session,r.subject_id,payload.knowledge_point_ids)
        await session.execute(delete(KnowledgePointLink).where(KnowledgePointLink.target_type=="mistake_draft",KnowledgePointLink.target_id==str(r.id)))
        for kp in payload.knowledge_point_ids: session.add(KnowledgePointLink(knowledge_point_id=kp,target_type="mistake_draft",target_id=str(r.id)))
        r.knowledge_point_ids=sorted(payload.knowledge_point_ids)
    r.item.version+=1; await session.flush(); await session.refresh(r.item); await session.refresh(r.draft); return r

async def reject_mistake_draft(session,item_id,version):
    r=await get_mistake_draft(session,item_id,True)
    if r.item.status=="rejected": return r
    if r.item.status=="converted": raise MistakeConflict("Converted draft cannot be rejected")
    if r.item.version!=version: raise MistakeConflict("Draft version conflict")
    r.item.status="rejected"; r.item.version+=1; await session.flush(); await session.refresh(r.item); return r

async def get_mistake(session,mistake_id):
    m=await session.get(Mistake,mistake_id)
    if not m: raise MistakeNotFound("Mistake not found")
    ri=(await session.execute(select(ReviewItem).where(ReviewItem.target_type=="mistake",ReviewItem.target_id==str(m.id)))).scalar_one()
    return MistakeRecord(m,await _links(session,"mistake",m.id),ri.id)

async def list_mistakes(session,status=None):
    stmt=select(Mistake)
    if status: stmt=stmt.where(Mistake.status==status)
    rows=(await session.execute(stmt.order_by(Mistake.updated_at.desc()))).scalars().all()
    return [await get_mistake(session,x.id) for x in rows]

async def convert_mistake_draft(session,item_id,version):
    r=await get_mistake_draft(session,item_id,True)
    if r.item.status=="converted":
        try:
            target_id = uuid.UUID(r.item.target_id or "")
        except (ValueError, AttributeError) as error:
            raise MistakeConflict("Converted draft has an invalid target") from error
        target = await session.get(Mistake, target_id)
        if target is None or target.source_draft_item_id != r.item.id:
            raise MistakeConflict("Converted draft target is inconsistent")
        try:
            return await get_mistake(session, target_id)
        except MistakeError as error:
            raise MistakeConflict("Converted draft target is incomplete") from error
    if r.item.status=="rejected": raise MistakeConflict("Rejected draft cannot be converted")
    if r.item.version!=version: raise MistakeConflict("Draft version conflict")
    question_id=r.question_id
    if question_id is None:
        qdraft=await session.get(QuestionDraft,r.question_draft_id)
        source_item=await session.get(DraftItem,qdraft.draft_item_id)
        if (
            qdraft is None
            or source_item is None
            or source_item.status != "converted"
            or source_item.target_type != "question"
            or not source_item.target_id
        ):
            raise MistakeConflict("Question draft must be converted first")
        try:
            question_id=uuid.UUID(source_item.target_id)
        except ValueError as error:
            raise MistakeConflict("Question draft conversion target is invalid") from error
        if await session.get(Question, question_id) is None:
            raise MistakeConflict("Question draft conversion target is missing")
    m=Mistake(source_draft_item_id=r.item.id,question_id=question_id,subject_id=r.subject_id,title=r.title,
        question_text=r.question_text,my_answer=r.my_answer,correct_answer=r.correct_answer_snapshot,
        analysis=r.explanation_snapshot,reason_category=r.reason_category,mistake_reason=r.mistake_reason,
        difficulty=r.difficulty,status="active",visibility="private",version=1)
    session.add(m); await session.flush()
    for kp in r.knowledge_point_ids: session.add(KnowledgePointLink(knowledge_point_id=kp,target_type="mistake",target_id=str(m.id)))
    ri=ReviewItem(target_type="mistake",target_id=str(m.id),state="active")
    session.add(ri); r.item.status="converted"; r.item.target_type="mistake"; r.item.target_id=str(m.id); r.item.version+=1
    await session.flush(); await session.refresh(m); await session.refresh(ri)
    return MistakeRecord(m,sorted(r.knowledge_point_ids),ri.id)

async def update_mistake(session,mistake_id,payload:MistakeUpdate):
    r=await get_mistake(session,mistake_id)
    if r.version!=payload.version: raise MistakeConflict("Mistake version conflict")
    for k,v in payload.model_dump(exclude={"version","knowledge_point_ids"},exclude_unset=True).items(): setattr(r.mistake,k,v)
    if payload.knowledge_point_ids is not None:
        await _validate_points(session,r.subject_id,payload.knowledge_point_ids)
        await session.execute(delete(KnowledgePointLink).where(KnowledgePointLink.target_type=="mistake",KnowledgePointLink.target_id==str(r.id)))
        for kp in payload.knowledge_point_ids: session.add(KnowledgePointLink(knowledge_point_id=kp,target_type="mistake",target_id=str(r.id)))
    r.mistake.version+=1; await session.flush(); return await get_mistake(session,mistake_id)

async def archive_mistake(session,mistake_id,version):
    r=await get_mistake(session,mistake_id)
    if r.status=="archived": return r
    if r.version!=version: raise MistakeConflict("Mistake version conflict")
    r.mistake.status="archived"; r.mistake.version+=1
    ri=await session.get(ReviewItem,r.review_item_id); ri.state="paused"
    await session.flush(); return await get_mistake(session,mistake_id)
