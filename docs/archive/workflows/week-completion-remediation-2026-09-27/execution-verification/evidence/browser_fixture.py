import asyncio,json,uuid
from pathlib import Path
from sqlalchemy import select
from app.database import async_session,engine
from app.config import get_settings
from app.utils.scratch_db_safety import require_scratch_database
from app.models.note import Note
from app.models.note_knowledge_point import NoteKnowledgePoint
from app.models.attachment import Attachment
from app.models.capture import CaptureItem
from app.schemas.taxonomy import SubjectCreate,KnowledgePointCreate
from app.schemas.question import QuestionCreate
from app.services import taxonomy_service as tax,question_service as qs,attempt_service as ats,mistake_service as ms
require_scratch_database(get_settings().DATABASE_URL)
async def main():
 async with async_session() as s:
  subject=await tax.create_subject(s,SubjectCreate(name='Browser Verify '+uuid.uuid4().hex[:8]))
  kp=await tax.create_knowledge_point(s,KnowledgePointCreate(subject_id=subject.id,name='Browser KP'))
  q=await qs.create_question(s,QuestionCreate(subject_id=subject.id,stem_md='VERIFY MULTIPLE CHOICE R01',question_type='multiple_choice',options=[{'key':v,'text':v+' option'} for v in ['A','B','C']],answer_data={'kind':'multiple_choice','value':['A','C']},knowledge_point_links=[{'knowledge_point_id':kp.id}]))
  attempt=await ats.submit_attempt(s,q.id,submitted_answer='B')
  draft=await ms.get_mistake_draft(s,attempt.mistake_draft_item_id)
  mistake=await ms.convert_mistake_draft(s,draft.item.id,draft.item.version)
  kp2=await tax.create_knowledge_point(s,KnowledgePointCreate(subject_id=subject.id,name='Legacy frozen KP'))
  n=Note(slug='frozen-http-'+uuid.uuid4().hex,title='Legacy KP freeze',content='',type='mistake');s.add(n);await s.flush()
  s.add(NoteKnowledgePoint(note_id=n.id,knowledge_point_id=kp2.id))
  att=Attachment(original_name='verify.png',display_name='verify.png',storage_key='verify/'+uuid.uuid4().hex+'.png',mime_type='image/png',size_bytes=1,checksum_sha256='0'*64)
  s.add(att);await s.flush();cap=CaptureItem(source_attachment_id=att.id,status='uploaded',subject_id=subject.id);s.add(cap);await s.flush()
  data={'question_id':str(q.id),'review_item_id':str(mistake.review_item_id),'kp_id':kp.id,'legacy_kp_id':kp2.id,'legacy_note_id':str(n.id),'capture_id':str(cap.id),'subject_id':subject.id}
  await s.commit()
 Path(__file__).with_name('browser-fixture.json').write_text(json.dumps(data,indent=2)+'\n')
 print(json.dumps(data))
 await engine.dispose()
asyncio.run(main())
