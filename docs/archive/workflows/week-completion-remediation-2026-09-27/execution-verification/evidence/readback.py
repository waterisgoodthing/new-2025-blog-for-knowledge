import asyncio,json
from pathlib import Path
from sqlalchemy import select,func
from app.database import async_session,engine
from app.models.note_knowledge_point import NoteKnowledgePoint
from app.models.ai_run import AiRun
from app.models.capture import CaptureItem
from app.utils.scratch_db_safety import require_scratch_database
from app.config import get_settings
require_scratch_database(get_settings().DATABASE_URL)
f=json.loads(Path("../docs/workflows/week-completion-remediation-2026-09-27/execution-verification/evidence/browser-fixture.json").read_text())
async def main():
 async with async_session() as s:
  print(json.dumps({"legacy_links_after_authenticated_delete":await s.scalar(select(func.count()).select_from(NoteKnowledgePoint).where(NoteKnowledgePoint.note_id==f["legacy_note_id"])),"capture_ai_runs":await s.scalar(select(func.count()).select_from(AiRun).where(AiRun.target_id==f["capture_id"]))}))
 await engine.dispose()
asyncio.run(main())
