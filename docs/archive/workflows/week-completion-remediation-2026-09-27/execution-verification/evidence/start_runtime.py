import sys,socket,json,subprocess,time,urllib.request
from pathlib import Path
sys.argv=['runtime','runtime']
import run_checks as r
state=r.state
for name in ['api_port','web_port']:
 s=socket.socket();s.bind(('127.0.0.1',0));state[name]=s.getsockname()[1];s.close()
r.env.update(ENV='development',ALLOWED_ORIGINS=f"http://127.0.0.1:{state['web_port']}",NEXT_PUBLIC_API_URL=f"http://127.0.0.1:{state['api_port']}",UPLOAD_ROOT=state['root']+'/uploads')
assert r.run('browser-seed',[str(r.ROOT/'backend/.venv/bin/python'),str(r.ROOT/'tests/e2e/seed/seed_week4_business.py')],r.ROOT/'backend')==0
for name,args,cwd in [('backend',[str(r.ROOT/'backend/.venv/bin/python'),'-m','uvicorn','main:app','--host','127.0.0.1','--port',str(state['api_port'])],r.ROOT/'backend'),('frontend',['/opt/homebrew/opt/node@24/bin/node',str(r.ROOT/'node_modules/next/dist/bin/next'),'dev','--hostname','127.0.0.1','--port',str(state['web_port'])],r.ROOT)]:
 f=(r.OUT/(name+'-runtime.txt')).open('w')
 proc=subprocess.Popen(args,cwd=cwd,env=r.env,stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
 state[name+'_pid']=proc.pid
(r.OUT/'local-environment.json').write_text(json.dumps(state,indent=2)+'\n')
print('local runtime started',state['api_port'],state['web_port'])
