import asyncio,os,subprocess
from pathlib import Path
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine,async_sessionmaker
from app.utils.scratch_db_safety import require_scratch_database
from app.services import webauthn_challenge_service as svc
url=os.environ['DATABASE_URL']; require_scratch_database(url)
root=Path('/Users/limengyang/2025-blog-public'); out=Path('/tmp/week4-reassessment-backend')
async def concurrency():
    engine=create_async_engine(url); factory=async_sessionmaker(engine,expire_on_commit=False)
    async with factory() as s:
        await svc.store_challenge(s,b'isolated-concurrency-probe','operator_registration',session_id='reassessment-concurrency')
        await s.commit()
    async def consume():
        async with factory() as s:
            row=await svc.get_valid_challenge(s,'operator_registration',session_id='reassessment-concurrency')
            if row:
                await asyncio.sleep(0.1)
                await svc.mark_consumed(s,row)
            await s.commit()
            return row is not None
    result=await asyncio.gather(consume(),consume())
    print('real concurrent consume:',result,'single success=',sum(result)==1,flush=True)
    assert sum(result)==1
    async with factory() as s:
        await svc.store_challenge(s,b'isolated-live-migration-probe','operator_registration',session_id='reassessment-live')
        await s.commit()
    await engine.dispose()
asyncio.run(concurrency())
py=str(root/'backend/.venv/bin/python')
p=subprocess.run([py,'-m','alembic','downgrade','032'],cwd=root/'backend',capture_output=True,text=True)
(out/'downgrade-live.log').write_text(p.stdout+p.stderr)
print('downgrade with live challenge rejected=',p.returncode!=0 and 'refusing fail-closed downgrade' in p.stderr,flush=True)
assert p.returncode!=0 and 'refusing fail-closed downgrade' in p.stderr
async def verify_and_expire():
    engine=create_async_engine(url)
    async with engine.begin() as c:
        revision=await c.scalar(text('SELECT version_num FROM alembic_version'))
        print('revision after rejected downgrade=',revision,flush=True)
        assert revision=='033'
        await c.execute(text("UPDATE webauthn_challenges SET expires_at=now()-interval '1 hour'"))
    await engine.dispose()
asyncio.run(verify_and_expire())
for args in [('downgrade','032'),('upgrade','head')]:
    p=subprocess.run([py,'-m','alembic',*args],cwd=root/'backend',capture_output=True,text=True)
    (out/('expired-'+args[0]+'.log')).write_text(p.stdout+p.stderr)
    print(args,'exit=',p.returncode,flush=True)
    assert p.returncode==0
