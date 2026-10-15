import asyncio,json,sys,uuid
from pathlib import Path
from sqlalchemy import text,select,func
from app.database import engine,async_session
from app.utils.scratch_db_safety import require_scratch_database
from app.config import get_settings
require_scratch_database(get_settings().DATABASE_URL)
sys.path.insert(0,str(Path(__file__).resolve().parents[5]/'backend/tests'))
from test_f04_schema_ownership import _missing_manifest_objects,_orm_diff
from app.models.ai_run import AiRun
from app.models.note import Note
from app.models.note_knowledge_point import NoteKnowledgePoint
from app.schemas.taxonomy import SubjectCreate,KnowledgePointCreate
from app.schemas.question import QuestionCreate
from app.schemas.mistake import MistakeDraftCreate
from app.services import ai_run_service as ai,taxonomy_service as tax,question_service as qs,mistake_service as ms

def out(x): print(json.dumps(x,default=str),flush=True)
async def main():
 async with engine.connect() as c:
  for label,ddl in [('sql_column_type','ALTER TABLE public.draft_items ALTER COLUMN conversion_sequence TYPE bigint'),('challenge_check','ALTER TABLE public.webauthn_challenges DROP CONSTRAINT ck_webauthn_challenges_purpose'),('disabled_guard','ALTER TABLE public.legacy_note_migrations DISABLE TRIGGER trg_lnm_guard')]:
   tr=await c.begin()
   try:
    await c.execute(text(ddl))
    out({'probe':label,'catalog_gate':await _missing_manifest_objects(c),'orm_gate':str(await _orm_diff(c)),'expected':'at least one gate rejects drift'})
   finally: await tr.rollback()
 async with async_session() as s:
  subj=await tax.create_subject(s,SubjectCreate(name='verify-'+uuid.uuid4().hex[:8]))
  kp=await tax.create_knowledge_point(s,KnowledgePointCreate(subject_id=subj.id,name='legacy-only'))
  note=Note(slug='verify-'+uuid.uuid4().hex,title='legacy',content='',type='mistake')
  s.add(note);await s.flush();s.add(NoteKnowledgePoint(note_id=note.id,knowledge_point_id=kp.id));await s.flush()
  await tax.delete_knowledge_point(s,kp.id)
  count=await s.scalar(select(func.count()).select_from(NoteKnowledgePoint).where(NoteKnowledgePoint.note_id==note.id))
  out({'probe':'legacy_kp_delete_service','delete':'succeeded','remaining_links':count,'expected':'freeze or conflict; link preserved'})
  await s.rollback()
 async with async_session() as s:
  subj=await tax.create_subject(s,SubjectCreate(name='verify-ai-'+uuid.uuid4().hex[:8]))
  q=await qs.create_question(s,QuestionCreate(subject_id=subj.id,stem_md='UNRELATED QUESTION B',question_type='short_answer',answer_data={'kind':'short_answer','value':'B'}))
  run=await ai.start_ai_run(s,task_type='mistake_question_draft',input_summary='QUESTION A ONLY',review_required=True)
  await ai.complete_ai_run(s,run,output_data={'question_text':'QUESTION A ONLY'},validation_status='passed')
  draft=await ms.create_mistake_draft(s,MistakeDraftCreate(question_id=q.id,my_answer='x',source_run_id=run.id))
  out({'probe':'wrong_source_bind','draft_question':draft.question_text,'run_output':run.output_data,'linked':run.target_id==str(draft.draft.id),'expected':'source mismatch rejected'})
  await s.rollback()
 async with async_session() as s:
  run=await ai.start_ai_run(s,task_type='mistake_question_draft',review_required=True)
  await ai.complete_ai_run(s,run,output_data={},validation_status='passed');rid=run.id;await s.commit()
 async with async_session() as a,async_session() as b:
  # Retain objects so both sessions hold the pre-binding state in identity maps.
  ra=await a.get(AiRun,rid);rb=await b.get(AiRun,rid)
  id1,id2=uuid.uuid4(),uuid.uuid4()
  await ai.bind_run_to_entity(a,rid,entity_type='MistakeDraft',entity_id=id1);await a.commit()
  await ai.bind_run_to_entity(b,rid,entity_type='MistakeDraft',entity_id=id2);await b.commit()
 async with async_session() as s:
  result=await s.get(AiRun,rid)
  out({'probe':'stale_concurrent_bind','both_commits':'succeeded','last_target_wins':result.target_id==str(id2),'expected':'second bind conflicts'})
  await s.delete(result);await s.commit()
 await engine.dispose()
asyncio.run(main())
