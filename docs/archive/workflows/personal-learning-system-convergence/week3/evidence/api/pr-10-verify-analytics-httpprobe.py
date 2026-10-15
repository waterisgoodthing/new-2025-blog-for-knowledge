"""PR-10 verification: raw HTTP probe of the admin analytics endpoint.

Prints anonymous status, admin login status, and a sample JSON response body
so the response field names can be compared to the backend schema and the
W3-D05 contract by eye.

Run via the Week 3 guard:

    python3 scripts/week3-scratch-guard.py run --db-name astra_week3_pr10_verify \
        -- backend/.venv/bin/python docs/.../evidence/api/pr-10-verify-analytics-httpprobe.py
"""

from __future__ import annotations

import asyncio
import json
import os
import sys
import uuid

sys.path.insert(0, "backend")

from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy import text  # noqa: E402
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine  # noqa: E402

import main  # noqa: E402
from app.schemas.question import QuestionDraftCreate  # noqa: E402
from app.schemas.taxonomy import KnowledgePointCreate, SubjectCreate  # noqa: E402
from app.services.draft_service import (  # noqa: E402
    convert_question_draft,
    create_question_draft,
)
from app.services.taxonomy_service import (  # noqa: E402
    create_knowledge_point,
    create_subject,
)
from app.utils.auth import hash_password  # noqa: E402

PATH = "/api/admin/knowledge-points/analytics"
USERNAME = f"pr10-probe-{uuid.uuid4().hex[:8]}"
PASSWORD = "pr10-probe-pass-123"


async def _seed() -> None:
    engine = create_async_engine(os.environ["DATABASE_URL"])
    try:
        async with AsyncSession(engine) as session:
            await session.execute(
                text(
                    "INSERT INTO public.users (id,username,password_hash,is_admin) "
                    "VALUES (:id,:username,:password,true)"
                ),
                {"id": uuid.uuid4(), "username": USERNAME, "password": hash_password(PASSWORD)},
            )
            subject = await create_subject(
                session, SubjectCreate(name=f"probe-{uuid.uuid4().hex[:8]}")
            )
            kp = await create_knowledge_point(
                session,
                KnowledgePointCreate(subject_id=subject.id, name=f"probe-kp-{uuid.uuid4().hex[:8]}"),
            )
            draft = await create_question_draft(
                session,
                QuestionDraftCreate(
                    subject_id=subject.id,
                    question_text=f"probe {uuid.uuid4().hex[:8]}?",
                    question_type="short_answer",
                    correct_answer="a",
                    knowledge_point_ids=[kp.id],
                ),
            )
            await convert_question_draft(session, draft.item.id, version=1)
            await session.commit()
    finally:
        await engine.dispose()


def main_probe() -> None:
    asyncio.run(_seed())
    with TestClient(main.app) as client:
        anon = client.get(PATH)
        print(f"anonymous GET {PATH} -> {anon.status_code}")

        bad = client.post("/api/auth/login", json={"username": USERNAME, "password": "wrong"})
        print(f"admin login (wrong password) -> {bad.status_code}")

        login = client.post("/api/auth/login", json={"username": USERNAME, "password": PASSWORD})
        print(f"admin login -> {login.status_code}")
        assert login.status_code == 200, login.text

        resp = client.get(PATH)
        print(f"admin GET {PATH} -> {resp.status_code}")
        body = resp.json()
        print(f"payload rows = {len(body)}")
        sample = next((row for row in body if row["knowledge_point_id"]), body[0] if body else {})
        print("sample row keys =", sorted(sample.keys()))
        print("sample row =", json.dumps(sample, sort_keys=True))


if __name__ == "__main__":
    main_probe()
