"""PR-15 WebAuthn challenge persistence lifecycle (real DB).

Runs against the scratch database supplied through ``DATABASE_URL`` (the
Week 4 scratch guard injects an ``astra_week4_*`` target). Each case builds its
own async engine inside a fresh event loop and disposes it, so no engine leaks
across loops.
"""

from __future__ import annotations

import asyncio
import base64
import hashlib
import json
import os
import time
import uuid

from sqlalchemy import delete, select, text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from app.models.webauthn_challenge import WebAuthnChallenge
from app.services import webauthn_challenge_service as svc


def _client_data(challenge_b64: str, *, kind: str = "webauthn.create") -> dict:
    payload = json.dumps(
        {"type": kind, "challenge": challenge_b64, "origin": "http://localhost"}
    ).encode("utf-8")
    encoded = base64.urlsafe_b64encode(payload).rstrip(b"=").decode()
    return {"response": {"clientDataJSON": encoded}}


def _run(body):
    async def _main():
        engine = create_async_engine(os.environ["DATABASE_URL"])
        try:
            async with AsyncSession(engine, expire_on_commit=False) as session:
                await session.execute(delete(WebAuthnChallenge))
                await session.flush()
                result = await body(session)
                await session.commit()
                return result
        finally:
            await engine.dispose()

    return asyncio.run(_main())


def _rows(session):
    return (
        select(WebAuthnChallenge)
        .order_by(WebAuthnChallenge.created_at.asc())
    )


def test_store_get_consume_roundtrip():
    async def body(session):
        record = await svc.store_challenge(session, b"raw-challenge-1", "registration")
        assert record.id is not None
        assert record.consumed_at is None
        assert record.challenge_hash == hashlib.sha256(b"raw-challenge-1").hexdigest()

        found = await svc.get_valid_challenge(session, "registration")
        assert found is not None
        assert found.id == record.id

        await svc.mark_consumed(session, found)
        assert found.consumed_at is not None
        await session.commit()

        assert await svc.get_valid_challenge(session, "registration") is None

    _run(body)


def test_expired_challenge_is_rejected():
    async def body(session):
        await svc.store_challenge(session, b"ttl-one", "registration", ttl_seconds=1)
        await session.commit()
        time.sleep(1.2)
        assert await svc.get_valid_challenge(session, "registration") is None

    _run(body)


def test_consumed_challenge_cannot_be_reused():
    async def body(session):
        await svc.store_challenge(session, b"single-use", "authentication")
        await session.commit()
        first = await svc.get_valid_challenge(session, "authentication")
        assert first is not None
        await svc.mark_consumed(session, first)
        await session.commit()
        assert await svc.get_valid_challenge(session, "authentication") is None

    _run(body)


def test_cross_purpose_lookup_is_rejected():
    async def body(session):
        await svc.store_challenge(session, b"purpose-bound", "registration")
        await session.commit()
        assert await svc.get_valid_challenge(session, "authentication") is None
        assert await svc.get_valid_challenge(session, "operator_registration") is None
        assert await svc.get_valid_challenge(session, "registration") is not None

    _run(body)


def test_operator_session_binding_mismatch_is_rejected():
    async def body(session):
        await svc.store_challenge(
            session, b"operator-bound", "operator_registration", session_id="session-A"
        )
        await session.commit()
        assert (
            await svc.get_valid_challenge(
                session, "operator_registration", session_id="session-B"
            )
            is None
        )
        assert (
            await svc.get_valid_challenge(
                session, "operator_registration", session_id="session-A"
            )
            is not None
        )

    _run(body)


def test_user_binding_mismatch_is_rejected():
    async def body(session):
        user_a = uuid.uuid4()
        user_b = uuid.uuid4()
        await session.execute(
            text(
                "INSERT INTO public.users (id, username, password_hash, is_admin) "
                "VALUES (:i, :u, 'x', false)"
            ),
            {"i": user_a, "u": f"w4p15-a-{user_a.hex[:8]}"},
        )
        await session.execute(
            text(
                "INSERT INTO public.users (id, username, password_hash, is_admin) "
                "VALUES (:i, :u, 'x', false)"
            ),
            {"i": user_b, "u": f"w4p15-b-{user_b.hex[:8]}"},
        )
        await session.flush()

        await svc.store_challenge(
            session, b"user-bound", "registration", user_id=user_a
        )
        await session.commit()
        assert (
            await svc.get_valid_challenge(session, "registration", user_id=user_b)
            is None
        )
        assert (
            await svc.get_valid_challenge(session, "registration", user_id=user_a)
            is not None
        )

    _run(body)


def test_concurrent_ceremonies_store_independent_rows():
    async def body(session):
        await svc.store_challenge(session, b"concurrent-1", "registration")
        await svc.store_challenge(session, b"concurrent-2", "registration")
        await session.commit()
        records = (await session.execute(_rows(session))).scalars().all()
        assert len(records) == 2
        hashes = {r.challenge_hash for r in records}
        assert len(hashes) == 2

    _run(body)


def test_cleanup_removes_expired_only():
    async def body(session):
        await svc.store_challenge(session, b"stale", "registration", ttl_seconds=1)
        await svc.store_challenge(session, b"fresh", "registration", ttl_seconds=300)
        await session.commit()
        time.sleep(1.2)

        removed = await svc.cleanup_expired_challenges(session)
        await session.commit()

        assert removed == 1
        remaining = (await session.execute(_rows(session))).scalars().all()
        assert len(remaining) == 1
        assert remaining[0].challenge_hash == hashlib.sha256(b"fresh").hexdigest()

    _run(body)


def test_store_opportunistically_cleans_expired_rows():
    async def body(session):
        await svc.store_challenge(session, b"stale", "registration", ttl_seconds=1)
        await session.commit()
        time.sleep(1.2)

        await svc.store_challenge(session, b"fresh", "registration", ttl_seconds=300)
        await session.commit()

        records = (await session.execute(_rows(session))).scalars().all()
        assert len(records) == 1
        assert records[0].challenge_hash == hashlib.sha256(b"fresh").hexdigest()

    _run(body)


def test_store_survives_opportunistic_cleanup_failure(monkeypatch):
    async def boom(db, before=None):
        raise RuntimeError("simulated cleanup failure")

    monkeypatch.setattr(svc, "cleanup_expired_challenges", boom)

    async def body(session):
        record = await svc.store_challenge(session, b"resilient", "registration")
        await session.commit()

        assert record.id is not None
        records = (await session.execute(_rows(session))).scalars().all()
        assert len(records) == 1
        assert records[0].challenge_hash == hashlib.sha256(b"resilient").hexdigest()

    _run(body)


def _hash(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def test_client_challenge_extraction_roundtrip_and_malformed():
    raw = b"roundtrip-challenge-bytes"
    challenge_b64 = base64.urlsafe_b64encode(raw).rstrip(b"=").decode()

    credential = _client_data(challenge_b64)
    assert svc.client_challenge_bytes(credential) == raw
    assert svc.challenge_hash_from_credential(credential) == _hash(raw)

    assert svc.client_challenge_bytes(None) is None
    assert svc.challenge_hash_from_credential({"response": {}}) is None
    assert svc.challenge_hash_from_credential({"response": {"clientDataJSON": "!!!"}}) is None
    assert svc.challenge_hash_from_credential(
        {
            "response": {
                "clientDataJSON": base64.urlsafe_b64encode(b"not-json")
                .rstrip(b"=")
                .decode()
            }
        }
    ) is None
    no_challenge = (
        base64.urlsafe_b64encode(json.dumps({"type": "webauthn.create"}).encode())
        .rstrip(b"=")
        .decode()
    )
    assert svc.challenge_hash_from_credential(
        {"response": {"clientDataJSON": no_challenge}}
    ) is None


def test_hash_lookup_matches_the_answered_challenge_not_the_latest():
    async def body(session):
        a = await svc.store_challenge(session, b"challenge-A", "registration")
        b = await svc.store_challenge(session, b"challenge-B", "registration")
        await session.commit()

        assert b.created_at >= a.created_at
        found_a = await svc.get_valid_challenge_by_hash(
            session, _hash(b"challenge-A"), "registration"
        )
        assert found_a is not None and found_a.id == a.id

        found_b = await svc.get_valid_challenge_by_hash(
            session, _hash(b"challenge-B"), "registration"
        )
        assert found_b is not None and found_b.id == b.id

    _run(body)


def test_hash_lookup_rejects_unknown_and_mismatched_rows():
    async def body(session):
        await svc.store_challenge(session, b"known-challenge", "registration")
        await session.commit()

        assert (
            await svc.get_valid_challenge_by_hash(
                session, _hash(b"unknown-challenge"), "registration"
            )
            is None
        )

    _run(body)


def test_hash_lookup_rejects_expired_consumed_and_cross_purpose():
    async def body(session):
        await svc.store_challenge(session, b"reg-challenge", "registration")
        await svc.store_challenge(session, b"auth-challenge", "authentication")
        await session.commit()

        assert (
            await svc.get_valid_challenge_by_hash(
                session, _hash(b"reg-challenge"), "authentication"
            )
            is None
        )

        record = await svc.get_valid_challenge_by_hash(
            session, _hash(b"reg-challenge"), "registration"
        )
        assert record is not None
        await svc.mark_consumed(session, record)
        await session.commit()
        assert (
            await svc.get_valid_challenge_by_hash(
                session, _hash(b"reg-challenge"), "registration"
            )
            is None
        )

        await svc.store_challenge(session, b"expiring", "registration", ttl_seconds=1)
        await session.commit()
        time.sleep(1.2)
        assert (
            await svc.get_valid_challenge_by_hash(
                session, _hash(b"expiring"), "registration"
            )
            is None
        )

    _run(body)


def test_hash_lookup_enforces_session_and_user_binding():
    async def body(session):
        user_a = uuid.uuid4()
        user_b = uuid.uuid4()
        for user in (user_a, user_b):
            await session.execute(
                text(
                    "INSERT INTO public.users (id, username, password_hash, is_admin) "
                    "VALUES (:i, :u, 'x', false)"
                ),
                {"i": user, "u": f"w4f03-{user.hex[:8]}"},
            )
        await session.flush()

        await svc.store_challenge(
            session, b"operator-challenge", "operator_registration", session_id="session-A"
        )
        await svc.store_challenge(
            session, b"user-challenge", "registration", user_id=user_a
        )
        await session.commit()

        assert (
            await svc.get_valid_challenge_by_hash(
                session,
                _hash(b"operator-challenge"),
                "operator_registration",
                session_id="session-B",
            )
            is None
        )
        assert (
            await svc.get_valid_challenge_by_hash(
                session,
                _hash(b"operator-challenge"),
                "operator_registration",
                session_id="session-A",
            )
            is not None
        )
        assert (
            await svc.get_valid_challenge_by_hash(
                session, _hash(b"user-challenge"), "registration", user_id=user_b
            )
            is None
        )
        assert (
            await svc.get_valid_challenge_by_hash(
                session, _hash(b"user-challenge"), "registration", user_id=user_a
            )
            is not None
        )

    _run(body)
