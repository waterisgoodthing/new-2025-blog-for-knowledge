"""PR-12 independent HTTP concurrency probe (PR-12-verify).

Isolated in its own module so the module-global async engine binds to a single
event loop for the whole process. Run ALONE:

    python3 scripts/week3-scratch-guard.py run --db-name astra_week3_pr12_verify \\
        -- backend/.venv/bin/python -m pytest tests/test_pr12_verify_concurrency.py -q

Two real parallel admin POSTs race the (note_id, knowledge_point_id) primary
key. Both must be answered 200 (idempotent), never 500.
"""

from __future__ import annotations

import asyncio
import os
import uuid

import httpx
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

import main
from app.utils.auth import hash_password

NOTE_KP = "/api/admin/notes/{note_id}/knowledge-points/{kp_id}"


async def _seed():
    engine = create_async_engine(os.environ["DATABASE_URL"])
    suffix = uuid.uuid4().hex[:8]
    try:
        async with AsyncSession(engine) as s:
            await s.execute(
                text(
                    "INSERT INTO public.users (id,username,password_hash,is_admin) "
                    "VALUES (:i,:u,:p,true)"
                ),
                {"i": uuid.uuid4(), "u": f"pr12vc-{suffix}", "p": hash_password("pr12vc-pass-123")},
            )
            sid = (await s.execute(text("INSERT INTO public.subjects(name) VALUES(:n) RETURNING id"), {"n": f"pr12vc-s-{suffix}"})).scalar_one()
            kp = (await s.execute(text("INSERT INTO public.knowledge_points(subject_id,name) VALUES(:s,:n) RETURNING id"), {"s": sid, "n": f"pr12vc-kp-{suffix}"})).scalar_one()
            note = (await s.execute(text(
                "INSERT INTO public.notes(id,slug,title,content,type,ef,interval,repetitions) "
                "VALUES(gen_random_uuid(),:slug,'t','c','note',2.5,0,0) RETURNING id"),
                {"slug": f"pr12vc-n-{suffix}"})).scalar_one()
            await s.commit()
    finally:
        await engine.dispose()
    return {"username": f"pr12vc-{suffix}", "password": "pr12vc-pass-123",
            "note_id": str(note), "kp_id": int(kp)}


def test_concurrent_http_duplicate_link_never_500():
    async def run():
        s = await _seed()
        async with main.lifespan(main.app):
            async with httpx.AsyncClient(
                transport=httpx.ASGITransport(app=main.app), base_url="http://test"
            ) as ac:
                login = await ac.post(
                    "/api/auth/login",
                    json={"username": s["username"], "password": s["password"]},
                )
                assert login.status_code == 200, login.text
                url = NOTE_KP.format(note_id=s["note_id"], kp_id=s["kp_id"])
                r1, r2 = await asyncio.gather(ac.post(url), ac.post(url))
                assert r1.status_code == 200, r1.text
                assert r2.status_code == 200, r2.text
                assert r1.json()["linked"] is True and r2.json()["linked"] is True
                assert (await ac.delete(url)).status_code == 204

    asyncio.run(run())
