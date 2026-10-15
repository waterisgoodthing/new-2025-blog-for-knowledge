import asyncio, os, threading, urllib.request
from sqlalchemy.ext.asyncio import create_async_engine,async_sessionmaker
from app.utils.scratch_db_safety import require_scratch_database,require_migration_target
from app.cli import create_registration_server
url=os.environ['DATABASE_URL'];require_scratch_database(url)
try:
    require_migration_target('postgresql+asyncpg://localhost:5432/blog_db')
except RuntimeError as e: print('CI migration guard: REJECTED before connection:',e,flush=True)
server=create_registration_server(0,'127.0.0.1',url)
thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
try:
    for i in range(2):
        try:
            with urllib.request.urlopen(f'http://127.0.0.1:{server.server_port}/api/passkey/register/options', timeout=10) as r:
                r.read(); print(f'actual CLI HTTP options request {i+1}: status={r.status}',flush=True)
        except Exception as e: print(f'actual CLI HTTP options request {i+1}: {type(e).__name__}: {e}',flush=True)
finally:
    server.shutdown();server.server_close();thread.join()
