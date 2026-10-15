import os, sys, subprocess
from pathlib import Path
ROOT=Path('/Users/limengyang/2025-blog-public'); OUT=Path('/tmp/week4-reassessment-backend'); PY=str(ROOT/'backend/.venv/bin/python'); GUARD=str(ROOT/'scripts/week4-scratch-guard.py')
name='astra_week4_reassess_20260926_'+sys.argv[1]
env=dict(os.environ, PYTHONPATH=str(ROOT/'backend'), DATABASE_URL=f'postgresql+asyncpg://localhost:5432/{name}', ENV='development', AUTH_BYPASS='false', AUTH_BYPASS_ALLOW='false', AI_API_KEY='', DASHSCOPE_API_KEY='', DEEPSEEK_API_KEY='', UPLOAD_ROOT=str(OUT/'uploads'), ALLOWED_ORIGINS='http://app.ci.test:18787')
for k in ['LSR03_DATABASE_URL','BLOG_APPROVED_MIGRATION_TARGET','PGHOSTADDR','PGSERVICE','PGSERVICEFILE','PGOPTIONS']:env.pop(k,None)
def run(label,args,check=True):
    cmd=[PY,GUARD,'run','--db-name',name,'--',*args]
    with (OUT/(label+'.log')).open('w') as f:
        p=subprocess.run(cmd,cwd=ROOT/'backend',env=env,stdout=f,stderr=subprocess.STDOUT)
    print(label,p.returncode,flush=True)
    if check and p.returncode:sys.exit(p.returncode)
    return p.returncode
if sys.argv[1]!='verify':run(sys.argv[1]+'-create',['createdb','-h','localhost','-p','5432',name])
run(sys.argv[1]+'-upgrade',[PY,'-m','alembic','upgrade','head'])
run(sys.argv[1]+'-head',[PY,'-m','alembic','heads'])
if sys.argv[1]=='e2e':
    run('e2e-seed',[PY,str(OUT/'seed.py')])
    os.chdir(ROOT/'backend')
    os.execve(PY,[PY,'-m','uvicorn','main:app','--host','127.0.0.1','--port','18001'],env)
if sys.argv[1]=='verify':
    run('verify-downgrade',[PY,'-m','alembic','downgrade','032'])
    run('verify-reupgrade',[PY,'-m','alembic','upgrade','head'])
    run('targeted',[PY,'-m','pytest','-p','no:cacheprovider','-q','tests/test_capture_taxonomy.py','tests/test_ocr_baseline.py','tests/test_webauthn_challenge_lifecycle.py','tests/test_passkey_ceremonies.py','tests/test_login_throttling.py','tests/test_login_throttling_integration.py','tests/test_ai_governance.py'],False)
if sys.argv[1]=='full':
    run('full-suite',[PY,'-m','pytest','-p','no:cacheprovider','tests/','-q','--tb=short','-rs'],False)
if sys.argv[1]=='isolation':
    run('excluded-isolated',[PY,'-m','pytest','-p','no:cacheprovider','-q','--tb=short','tests/test_pr09_verify_http.py::test_public_empty_envelope_explicit','tests/test_pr11_dashboard_service.py::DashboardPr11ServiceTest::test_all_empty_answers_are_honest','tests/test_pr11_dashboard_service.py::DashboardPr11ServiceTest::test_partial_service_failure_degrades_without_raising'],False)
