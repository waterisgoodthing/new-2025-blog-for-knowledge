import asyncio, base64, hashlib, json, sqlite3, uuid
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
import cbor2
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec
from sqlalchemy.dialects import sqlite
from app.services import passkey_service as ps, webauthn_challenge_service as cs, login_throttle as lt
from app.schemas.auth import LoginRequest
from app.routers.auth import login
from starlette.requests import Request
from fastapi import HTTPException

b64=lambda b:base64.urlsafe_b64encode(b).rstrip(b'=').decode()
conn=sqlite3.connect(':memory:')
conn.row_factory=sqlite3.Row
conn.execute('CREATE TABLE webauthn_challenges (id TEXT, challenge TEXT, challenge_hash TEXT, purpose TEXT, session_id TEXT, user_id TEXT, created_at TEXT, expires_at TEXT, consumed_at TEXT)')
class MemoryDb:
    async def execute(self, statement):
        sql=str(statement.compile(dialect=sqlite.dialect(),compile_kwargs={'literal_binds':True}))
        row=conn.execute(sql).fetchone()
        return SimpleNamespace(scalar_one_or_none=lambda:SimpleNamespace(**dict(row)) if row else None)
    def add(self, record):
        conn.execute('UPDATE webauthn_challenges SET consumed_at=? WHERE id=?',(str(record.consumed_at),record.id))
    async def flush(self): pass

def store(challenge, offset):
    now=datetime.now(timezone.utc)
    conn.execute('INSERT INTO webauthn_challenges VALUES (?,?,?,?,?,?,?,?,?)',(uuid.uuid4().hex,b64(challenge),hashlib.sha256(challenge).hexdigest(),'authentication',None,None,str(now+timedelta(seconds=offset)),str(now+timedelta(seconds=300)),None))

key=ec.generate_private_key(ec.SECP256R1())
nums=key.public_key().public_numbers()
pub=cbor2.dumps({1:2,3:-7,-1:1,-2:nums.x.to_bytes(32,'big'),-3:nums.y.to_bytes(32,'big')})
cred_id=b'review-credential'
def assertion(challenge):
    client=json.dumps({'type':'webauthn.get','challenge':b64(challenge),'origin':'http://localhost:2025'}).encode()
    authdata=hashlib.sha256(b'localhost').digest()+bytes([5])+(1).to_bytes(4,'big')
    sig=key.sign(authdata+hashlib.sha256(client).digest(),ec.ECDSA(hashes.SHA256()))
    return {'id':b64(cred_id),'rawId':b64(cred_id),'type':'public-key','response':{'clientDataJSON':b64(client),'authenticatorData':b64(authdata),'signature':b64(sig)}}

async def auth_probe():
    a=b'A'*32; b=b'B'*32
    db=MemoryDb()
    store(a,0)
    baseline=await ps.verify_authentication(db,assertion(a),b64(cred_id),pub,0,expected_origin='http://localhost:2025',expected_rp_id='localhost')
    conn.execute('DELETE FROM webauthn_challenges')
    store(a,0);store(b,1)
    after_b=await ps.verify_authentication(db,assertion(a),b64(cred_id),pub,0,expected_origin='http://localhost:2025',expected_rp_id='localhost')
    result_b=await ps.verify_authentication(db,assertion(b),b64(cred_id),pub,0,expected_origin='http://localhost:2025',expected_rp_id='localhost')
    after_b_consumed=await ps.verify_authentication(db,assertion(a),b64(cred_id),pub,0,expected_origin='http://localhost:2025',expected_rp_id='localhost')
    print('AUTH signed assertion baseline A:',baseline)
    print('AUTH same valid assertion A with newer B:',after_b)
    print('AUTH valid B:',result_b,'A after B consumed:',after_b_consumed)
    assert baseline==(True,1) and after_b==(False,0) and result_b==(True,1) and after_b_consumed==(True,1)

class NoUserDb:
    async def execute(self, statement):
        return SimpleNamespace(scalar_one_or_none=lambda:None)

async def account_probe():
    lt.reset_state()
    clock=[1000.0]
    lt._now=lambda:clock[0]
    lt._ip_ttl_seconds=lambda:3600
    for i in range(3):
        req=LoginRequest(username=f'nonexistent-{i}-'+('x'*100000),password='wrong')
        try:
            await login(req,Request({'type':'http','client':('192.0.2.55',1234),'headers':[]}),NoUserDb())
        except HTTPException as e:
            assert e.status_code==401
    retained=sum(len(k) for k in lt._accounts)
    clock[0]+=10_000_000
    lt.record_failure(None,'192.0.2.56')
    print('THROTTLE after 3 unauthenticated nonexistent-account requests: account_keys=',len(lt._accounts),'retained_username_bytes=',retained,'after 115 days account_keys=',len(lt._accounts),'IP_keys=',len(lt._ips))
    assert len(lt._accounts)==3 and retained>300000 and len(lt._ips)==1
    lt.reset_state()

asyncio.run(auth_probe())
asyncio.run(account_probe())
