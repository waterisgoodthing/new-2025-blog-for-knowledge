import asyncio,json,uuid
from sqlalchemy import select
import httpx
from main import app
from app.database import async_session,engine,get_db
from app.routers.auth import get_current_admin
from app.models.note import Note,User
from app.models.folder import Folder
from app.utils.scratch_db_safety import require_scratch_database
from app.config import get_settings
require_scratch_database(get_settings().DATABASE_URL)
async def main():
 async with async_session() as s:
  n=Note(slug='audit-freeze-'+uuid.uuid4().hex,title='audit only',content='synthetic',type='mistake',status='draft')
  f=Folder(name='audit-only',sort_order=0)
  s.add_all([n,f]);await s.flush()
  async def db(): yield s
  async def admin(): return User(id=uuid.uuid4(),username='audit-synthetic-admin')
  app.dependency_overrides[get_db]=db;app.dependency_overrides[get_current_admin]=admin
  async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app),base_url='http://audit.test') as c:
   r=await c.post('/api/ai/suggestions/execute',json={'type':'organize','action':'move_to_folder','targets':[n.slug],'folder_id':str(f.id)})
   await s.flush();await s.refresh(n)
   print(json.dumps({'http':r.status_code,'response':r.json(),'legacy_type':n.type,'folder_changed':n.folder_id==f.id,'scope':'ASGI admin dependency overridden; real handler/service/PG; transaction rollback'},ensure_ascii=False))
  app.dependency_overrides.clear();await s.rollback()
 await engine.dispose()
asyncio.run(main())
