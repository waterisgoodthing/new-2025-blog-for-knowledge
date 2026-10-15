from pathlib import Path
import os,sys,json,subprocess,time
ROOT=Path(__file__).resolve().parents[5]
OUT=Path(__file__).resolve().parent
state=json.loads((OUT/'local-environment.json').read_text())
env=os.environ.copy()
env.update(DATABASE_URL=f"postgresql+asyncpg://{__import__('getpass').getuser()}@127.0.0.1:{state['port']}/{state['db']}",PYTHONPATH=str(ROOT/'backend'),AUTH_BYPASS='false',AUTH_BYPASS_ALLOW='false',OCR_AUTO_RECOGNITION_ENABLED='false',AI_API_KEY='',DEEPSEEK_API_KEY='',DASHSCOPE_API_KEY='',KEEP_ALIVE_ENABLED='false',NEXT_TELEMETRY_DISABLED='1')
env['PATH']='/opt/homebrew/opt/node@24/bin:'+env['PATH']
def run(label,args,cwd):
 t=time.monotonic()
 with (OUT/(label+'.txt')).open('w') as f:
  r=subprocess.run(args,cwd=cwd,env=env,stdout=f,stderr=subprocess.STDOUT)
 print(json.dumps({'check':label,'exit':r.returncode,'seconds':round(time.monotonic()-t,2)}),flush=True)
 return r.returncode
mode=sys.argv[1]
if mode=='backend':
 if run('fresh-migration',['.venv/bin/python','-m','alembic','upgrade','head'],ROOT/'backend'):sys.exit(1)
 run('alembic-check',['.venv/bin/python','-m','alembic','check'],ROOT/'backend')
 run('targeted-backend',['.venv/bin/python','-m','pytest','tests/test_attempt_service.py','tests/test_f03_freeze_coverage.py','tests/test_f04_schema_ownership.py','tests/test_ai_governance.py','tests/test_capture_service.py','tests/test_i6_capture_failure_matrix.py','-q','-rs'],ROOT/'backend')
elif mode=='frontend':
 run('frontend-node24',['npm','test'],ROOT)
 run('typecheck-node24',['node','node_modules/typescript/bin/tsc','--noEmit','--incremental','false'],ROOT)
 run('test-typecheck-node24',['npm','run','test:typecheck','--','--incremental','false'],ROOT)
