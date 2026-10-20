#!/usr/bin/env python3
"""Week 4 recheck probes (read-only, no product code changes).

Independently reproduces the material reassessment findings against a local
scratch DB (`astra_week4_pr15`) and pure functions. Never connects to
blog_db / blog_v2.

Run:
  cd backend && DATABASE_URL="postgresql+asyncpg://limengyang@localhost:5432/astra_week4_pr15" \
    PYTHONPATH=. .venv/bin/python ../docs/workflows/personal-learning-system-convergence/week4/evidence/gate/recheck_probes.py
"""

import asyncio
import os
import sys
from datetime import datetime, timedelta, timezone

SCRATCH = os.environ.get("DATABASE_URL", "")
assert "astra_week4_" in SCRATCH, f"refusing non-scratch target: {SCRATCH}"


def probe_f01():
    print("== F01: CI guard rejects blog_db ==")
    from app.utils.scratch_db_safety import require_migration_target, require_scratch_database

    target = "postgresql+asyncpg://user:password@localhost:5432/blog_db"
    for name, fn in (("require_migration_target", require_migration_target), ("require_scratch_database", require_scratch_database)):
        try:
            fn(target, approved_target=None) if name == "require_migration_target" else fn(target)
            print(f"  {name}: ALLOWED (unexpected)")
        except RuntimeError as e:
            print(f"  {name}: REFUSED -> {str(e)[:70]}")


def probe_f02():
    print("== F02: one AsyncEngine reused across new event loops (cli.py pattern) ==")
    from sqlalchemy import text
    from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

    engine = create_async_engine(SCRATCH)
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async def _run():
        async with session_factory() as s:
            return (await s.execute(text("SELECT 1"))).scalar_one()

    def run_on_new_loop():
        loop = asyncio.new_event_loop()
        try:
            return loop.run_until_complete(_run())
        finally:
            loop.close()

    try:
        print("  request 1:", run_on_new_loop())
    except Exception as e:
        print("  request 1 ERROR:", type(e).__name__, str(e)[:120])
    try:
        print("  request 2:", run_on_new_loop())
    except Exception as e:
        print("  request 2 ERROR:", type(e).__name__, str(e)[:120])


async def probe_f03():
    print("== F03: verify selects LATEST challenge, not the matching one ==")
    from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

    from app.services import webauthn_challenge_service as wc

    engine = create_async_engine(SCRATCH)
    async with AsyncSession(engine) as db:
        await wc.cleanup_expired_challenges(db)
        a = await wc.store_challenge(db, b"A" * 32, wc.PURPOSE_AUTHENTICATION)
        got_a = await wc.get_valid_challenge(db, wc.PURPOSE_AUTHENTICATION)
        b = await wc.store_challenge(db, b"B" * 32, wc.PURPOSE_AUTHENTICATION)
        got_after_b = await wc.get_valid_challenge(db, wc.PURPOSE_AUTHENTICATION)
        print("  A id:", a.id, "hash:", a.challenge_hash[:12])
        print("  B id:", b.id, "hash:", b.challenge_hash[:12])
        print("  latest selected before B:", got_a.challenge_hash[:12], "(== A:", got_a.challenge_hash == a.challenge_hash, ")")
        print("  latest selected after B :", got_after_b.challenge_hash[:12], "(== B:", got_after_b.challenge_hash == b.challenge_hash, ")")
        print("  => A still unconsumed but a fresh A assertion would be verified against B (interference)")
        await db.rollback()
    await engine.dispose()


def probe_f05():
    print("== F05: lower-layer wrapped errors lose category ==")
    from app.services.capture_failure_taxonomy import categorize_provider_error

    samples = {
        "plain native timeout (str(ReadTimeout))": "ReadTimeout" ,
        "wrapped final RuntimeError (no keyword)": "All AI providers failed. Trail: dashscope_vision: ",
        "malformed JSON (ai_service)": "Failed to parse AI response: Expecting value: line 1 column 1 (char 0)",
    }
    for label, msg in samples.items():
        print(f"  {label!r:60} -> {categorize_provider_error(msg).value}")


def probe_f06():
    print("== F06: account throttle dict has no eviction / no length bound ==")
    from app.services import login_throttle as lt

    lt.reset_state()
    huge = "u" * 100_000
    lt.record_failure(huge, None)
    # advance clock far beyond any TTL; IP ttl sweep runs on IP writes only.
    print("  account entries after one huge-username failure:", len(lt._accounts))
    print("  account key length:", len(huge))
    lt.record_failure("other", "1.2.3.4")
    lt.record_failure("other2", "1.2.3.4")
    print("  account entries after unrelated failures (still retained):", len(lt._accounts))
    lt.reset_state()


if __name__ == "__main__":
    print("scratch target:", SCRATCH.replace("://", "://<redacted>@", 1) if "@" in SCRATCH else SCRATCH)
    probe_f01()
    probe_f02()
    asyncio.run(probe_f03())
    probe_f05()
    probe_f06()
    print("done")
