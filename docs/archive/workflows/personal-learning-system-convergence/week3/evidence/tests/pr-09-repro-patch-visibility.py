"""PR9F-06 standalone repro (verifier: PR-09-verify-rework).

Success-change PATCH /api/admin/mistakes/{id}/visibility must return 200 (not
500 MissingGreenlet) and version+1. Seeds FK-valid rows, then drives TestClient.
"""

from __future__ import annotations

import asyncio
import os
import uuid

from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine


async def _seed_mistake() -> str:
    engine = create_async_engine(os.environ["DATABASE_URL"])
    session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)()
    try:
        subject_id = (await session.execute(text(
            "INSERT INTO public.subjects (name, status) VALUES ('pr09-vfy-patch-subj','active') "
            "ON CONFLICT (name) DO UPDATE SET name=EXCLUDED.name RETURNING id"
        ))).scalar_one()
        draft_item_id = uuid.uuid4()
        await session.execute(text(
            "INSERT INTO public.draft_items (id,draft_type,source_type,status,version,validation_errors) "
            "VALUES (:id,'mistake','question','pending',1,'[]'::json)"
        ), {"id": draft_item_id})
        question_id = uuid.uuid4()
        await session.execute(text(
            "INSERT INTO public.questions (id,subject_id,stem_md,question_text,question_type,"
            "options,answer_data,status,visibility,version) "
            "VALUES (:qid,:sid,'','Q?','true_false','[]'::json,'{}'::json,'active','private',1)"
        ), {"qid": question_id, "sid": int(subject_id)})
        mistake_id = uuid.uuid4()
        await session.execute(text(
            "INSERT INTO public.mistakes (id,source_draft_item_id,question_id,subject_id,title,"
            "question_text,my_answer,correct_answer,analysis,reason_category,mistake_reason,"
            "difficulty,status,visibility,version) "
            "VALUES (:mid,:did,:qid,:sid,'Patch Title','Q?','secret','A','an','concept','reason',"
            "'easy','active','private',1)"
        ), {"mid": mistake_id, "did": draft_item_id, "qid": question_id, "sid": int(subject_id)})
        await session.execute(text(
            "INSERT INTO public.review_items (id,target_type,target_id,mistake_id,state,"
            "algorithm,interval_days,repetitions) "
            "VALUES (:rid,'mistake',:mid_str,:mid,'active','fixed_interval_v2',0,0)"
        ), {"rid": uuid.uuid4(), "mid_str": str(mistake_id), "mid": mistake_id})
        await session.commit()
        return str(mistake_id)
    finally:
        await session.rollback()
        await session.close()
        await engine.dispose()


async def _login_admin(client: TestClient) -> None:
    from app.utils.auth import hash_password

    username = f"pr09-vfy-patch-admin-{uuid.uuid4().hex[:8]}"
    password = "pr09-vfy-patch-pass-123"
    engine = create_async_engine(os.environ["DATABASE_URL"])
    session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)()
    try:
        user_id = uuid.uuid4()
        await session.execute(text(
            "INSERT INTO public.users (id,username,password_hash,is_admin) "
            "VALUES (:id,:un,:pw,true)"
        ), {"id": user_id, "un": username, "pw": hash_password(password)})
        await session.commit()
    finally:
        await session.rollback()
        await session.close()
        await engine.dispose()
    resp = client.post(
        "/api/auth/login",
        json={"username": username, "password": password},
    )
    assert resp.status_code == 200, resp.text


def main() -> int:
    import main as app_main

    mistake_id = asyncio.run(_seed_mistake())
    with TestClient(app_main.app) as client:
        asyncio.run(_login_admin(client))
        resp = client.patch(
            f"/api/admin/mistakes/{mistake_id}/visibility",
            json={"version": 1, "visibility": "public"},
        )
        print("PR9F-06 PATCH status:", resp.status_code)
        print("PR9F-06 PATCH body:", resp.text)
        ok = resp.status_code == 200
        if ok:
            body = resp.json()
            ok = body.get("visibility") == "public" and body.get("version") == 2
            print("PR9F-06 visibility:", body.get("visibility"), "version:", body.get("version"))
        print("RESULTS: PR9F-06:", "PASS" if ok else "FAIL")
        return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
