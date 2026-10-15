import asyncio, json
from sqlalchemy import select
from app.database import async_session,engine
from app.models.question import Question,QuestionKnowledgePoint
from app.models.review_item import ReviewItem
from app.services import attempt_service,mistake_service,review_item_service
from app.services.kp_analytics_service import get_knowledge_point_analytics
from app.services.reanswer_service import evaluate_answer
from app.utils.scratch_db_safety import require_scratch_database
from app.config import get_settings
require_scratch_database(get_settings().DATABASE_URL)
async def main():
 async with async_session() as s:
  q=(await s.execute(select(Question).where(Question.title=='E2E-W4-BUSINESS-Q'))).scalar_one()
  kp=(await s.execute(select(QuestionKnowledgePoint.knowledge_point_id).where(QuestionKnowledgePoint.question_id==q.id))).scalar_one()
  before=next(x for x in await get_knowledge_point_analytics(s) if x.knowledge_point_id==kp)
  a=await attempt_service.submit_attempt(s,q.id,submitted_answer='probe-wrong')
  d=await mistake_service.get_mistake_draft(s,a.mistake_draft_item_id)
  m=await mistake_service.convert_mistake_draft(s,d.item.id,d.item.version)
  ri=await s.get(ReviewItem,m.review_item_id)
  _,rec=await review_item_service.submit_review(s,ri.id,1,ri.next_review_at)
  after=next(x for x in await get_knowledge_point_analytics(s) if x.knowledge_point_id==kp)
  print(json.dumps({'question_kp':kp,'draft_kps':d.knowledge_point_ids,'mistake_kps':m.knowledge_point_ids,'record_created':str(rec.id),'metrics_before':before.model_dump(),'metrics_after':after.model_dump(),'transaction':'rolled back after observation'},ensure_ascii=False))
  q.question_type='multiple_choice';q.answer_data={'kind':'multiple_choice','value':['A','C']}
  print(json.dumps({'practice_A_C':attempt_service._is_correct(q,'A C'),'review_A_C':evaluate_answer(q.question_type,q.answer_data,'A C').verdict,'practice_lowercase':attempt_service._is_correct(q,'a,c'),'review_lowercase':evaluate_answer(q.question_type,q.answer_data,'a,c').verdict}))
  await s.rollback()
 await engine.dispose()
asyncio.run(main())
