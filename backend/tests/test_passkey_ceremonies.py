"""PR-15 / W4-F03 passkey ceremony integration with real DB challenge storage.

The ``webauthn`` library verification is stubbed (no authenticator, no network),
but every challenge is generated, persisted, matched by challenge hash, looked
up and consumed through the real ``webauthn_challenges`` table via the services.
Each synthetic credential carries a ``clientDataJSON`` whose ``challenge`` is
the server-generated one, so the hash-match path is genuinely exercised.

Run against the scratch database supplied through ``DATABASE_URL``.
"""

from __future__ import annotations

import asyncio
import base64
import hashlib
import json
import os

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from app.models.webauthn_challenge import WebAuthnChallenge
from app.services import passkey_service
from app.services import webauthn_challenge_service as challenge_service


class _RegistrationVerification:
    credential_id = b"credential-id-bytes"
    credential_public_key = b"public-key-bytes"
    sign_count = 7


class _AuthenticationVerification:
    new_sign_count = 11


_CALLS: dict[str, object] = {"expected_challenge": None}
_FAIL: dict[str, bool] = {"registration": False, "authentication": False}


def _fake_registration_response(**kwargs):
    _CALLS["expected_challenge"] = kwargs["expected_challenge"]
    if _FAIL["registration"]:
        raise ValueError("stubbed registration failure")
    return _RegistrationVerification()


def _fake_authentication_response(**kwargs):
    _CALLS["expected_challenge"] = kwargs["expected_challenge"]
    if _FAIL["authentication"]:
        raise ValueError("stubbed authentication failure")
    return _AuthenticationVerification()


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


def _decode(value: str) -> bytes:
    padding = 4 - len(value) % 4
    if padding != 4:
        value += "=" * padding
    return base64.urlsafe_b64decode(value)


def _credential(challenge_b64: str, *, kind: str = "webauthn.create") -> dict:
    payload = json.dumps(
        {"type": kind, "challenge": challenge_b64, "origin": "http://localhost"}
    ).encode("utf-8")
    client_data = base64.urlsafe_b64encode(payload).rstrip(b"=").decode()
    return {
        "id": "att",
        "rawId": "att",
        "type": "public-key",
        "response": {"clientDataJSON": client_data, "attestationObject": "x"},
    }


async def _consumed_by_hash(session, raw: bytes) -> bool | None:
    target = hashlib.sha256(raw).hexdigest()
    rows = (await session.execute(select(WebAuthnChallenge))).scalars().all()
    for row in rows:
        if row.challenge_hash == target:
            return row.consumed_at is not None
    return None


def test_registration_ceremony_stores_then_consumes_on_success(monkeypatch):
    monkeypatch.setattr("webauthn.verify_registration_response", _fake_registration_response)
    _FAIL["registration"] = False

    async def body(session):
        options = await passkey_service.generate_registration_options(session)
        raw = _decode(options["publicKey"]["challenge"])
        credential = _credential(options["publicKey"]["challenge"])

        stored = (await session.execute(select(WebAuthnChallenge))).scalars().one()
        assert stored.purpose == "registration"
        assert stored.session_id is None
        assert stored.user_id is None
        assert stored.consumed_at is None

        first = await passkey_service.verify_registration(session, credential)
        assert first is not None
        assert _CALLS["expected_challenge"] == raw
        await session.flush()
        stored = (await session.execute(select(WebAuthnChallenge))).scalars().one()
        assert stored.consumed_at is not None

        assert await passkey_service.verify_registration(session, credential) is None

    _run(body)


def test_registration_failure_does_not_consume_challenge(monkeypatch):
    monkeypatch.setattr("webauthn.verify_registration_response", _fake_registration_response)
    _FAIL["registration"] = True

    async def body(session):
        options = await passkey_service.generate_registration_options(session)
        credential = _credential(options["publicKey"]["challenge"])
        assert await passkey_service.verify_registration(session, credential) is None
        await session.flush()
        stored = (await session.execute(select(WebAuthnChallenge))).scalars().one()
        assert stored.consumed_at is None

        _FAIL["registration"] = False
        assert await passkey_service.verify_registration(session, credential) is not None
        await session.flush()
        stored = (await session.execute(select(WebAuthnChallenge))).scalars().one()
        assert stored.consumed_at is not None

    _run(body)


def test_registration_missing_or_forged_client_challenge_is_rejected(monkeypatch):
    monkeypatch.setattr("webauthn.verify_registration_response", _fake_registration_response)
    _FAIL["registration"] = False

    async def body(session):
        options = await passkey_service.generate_registration_options(session)
        pending = options["publicKey"]["challenge"]

        assert await passkey_service.verify_registration(session, {"id": "no-client-data"}) is None

        forged = base64.urlsafe_b64encode(b"forged-challenge-bytes").rstrip(b"=").decode()
        assert await passkey_service.verify_registration(session, _credential(forged)) is None

        await session.flush()
        assert await _consumed_by_hash(session, _decode(pending)) is False

    _run(body)


def test_registration_ab_ceremonies_verify_against_their_own_challenge(monkeypatch):
    monkeypatch.setattr("webauthn.verify_registration_response", _fake_registration_response)
    _FAIL["registration"] = False

    async def body(session):
        opts_a = await passkey_service.generate_registration_options(session)
        opts_b = await passkey_service.generate_registration_options(session)
        a_challenge = opts_a["publicKey"]["challenge"]
        b_challenge = opts_b["publicKey"]["challenge"]

        result_a = await passkey_service.verify_registration(session, _credential(a_challenge))
        assert result_a is not None
        assert _CALLS["expected_challenge"] == _decode(a_challenge)
        await session.flush()
        assert await _consumed_by_hash(session, _decode(a_challenge)) is True
        assert await _consumed_by_hash(session, _decode(b_challenge)) is False

        result_b = await passkey_service.verify_registration(session, _credential(b_challenge))
        assert result_b is not None
        assert _CALLS["expected_challenge"] == _decode(b_challenge)

    _run(body)


def test_operator_registration_is_session_bound_and_consumed_before_verify(monkeypatch):
    monkeypatch.setattr("webauthn.verify_registration_response", _fake_registration_response)
    _FAIL["registration"] = True

    async def body(session):
        options = await passkey_service.generate_operator_registration_options(
            session, "session-A"
        )
        raw = _decode(options["publicKey"]["challenge"])
        credential = _credential(options["publicKey"]["challenge"])
        stored = (await session.execute(select(WebAuthnChallenge))).scalars().one()
        assert stored.purpose == "operator_registration"
        assert stored.session_id == "session-A"
        assert stored.user_id is None

        assert (
            await passkey_service.verify_operator_registration(
                session, credential, session_id="session-B"
            )
            is None
        )
        await session.flush()
        stored = (await session.execute(select(WebAuthnChallenge))).scalars().one()
        assert stored.consumed_at is None

        result = await passkey_service.verify_operator_registration(
            session, credential, session_id="session-A"
        )
        assert result is None
        assert _CALLS["expected_challenge"] == raw
        await session.flush()
        stored = (await session.execute(select(WebAuthnChallenge))).scalars().one()
        assert stored.consumed_at is not None

    _run(body)


def test_authentication_ceremony_consumes_on_success(monkeypatch):
    monkeypatch.setattr(
        "webauthn.verify_authentication_response", _fake_authentication_response
    )
    _FAIL["authentication"] = True

    async def body(session):
        options = await passkey_service.generate_authentication_options(session)
        raw = _decode(options["publicKey"]["challenge"])
        assertion = _credential(options["publicKey"]["challenge"], kind="webauthn.get")
        stored = (await session.execute(select(WebAuthnChallenge))).scalars().one()
        assert stored.purpose == "authentication"

        ok, count = await passkey_service.verify_authentication(
            session, assertion, "credential-id", b"public-key-bytes", 5
        )
        assert ok is False
        assert count == 5
        await session.flush()
        stored = (await session.execute(select(WebAuthnChallenge))).scalars().one()
        assert stored.consumed_at is None

        _FAIL["authentication"] = False
        ok, count = await passkey_service.verify_authentication(
            session, assertion, "credential-id", b"public-key-bytes", 5
        )
        assert ok is True
        assert count == 11
        assert _CALLS["expected_challenge"] == raw
        await session.flush()
        stored = (await session.execute(select(WebAuthnChallenge))).scalars().one()
        assert stored.consumed_at is not None

    _run(body)


def test_authentication_ab_ceremonies_verify_against_their_own_challenge(monkeypatch):
    monkeypatch.setattr(
        "webauthn.verify_authentication_response", _fake_authentication_response
    )
    _FAIL["authentication"] = False

    async def body(session):
        opts_a = await passkey_service.generate_authentication_options(session)
        opts_b = await passkey_service.generate_authentication_options(session)
        a_challenge = opts_a["publicKey"]["challenge"]
        b_challenge = opts_b["publicKey"]["challenge"]

        ok, count = await passkey_service.verify_authentication(
            session,
            _credential(a_challenge, kind="webauthn.get"),
            "credential-id",
            b"public-key-bytes",
            5,
        )
        assert ok is True and count == 11
        assert _CALLS["expected_challenge"] == _decode(a_challenge)
        await session.flush()
        assert await _consumed_by_hash(session, _decode(a_challenge)) is True
        assert await _consumed_by_hash(session, _decode(b_challenge)) is False

        ok, count = await passkey_service.verify_authentication(
            session,
            _credential(b_challenge, kind="webauthn.get"),
            "credential-id",
            b"public-key-bytes",
            5,
        )
        assert ok is True
        assert _CALLS["expected_challenge"] == _decode(b_challenge)

    _run(body)


def test_authentication_mismatched_challenge_is_rejected(monkeypatch):
    monkeypatch.setattr(
        "webauthn.verify_authentication_response", _fake_authentication_response
    )

    async def body(session):
        opts = await passkey_service.generate_authentication_options(session)
        pending = opts["publicKey"]["challenge"]
        forged = base64.urlsafe_b64encode(b"forged-auth-challenge").rstrip(b"=").decode()

        ok, count = await passkey_service.verify_authentication(
            session,
            _credential(forged, kind="webauthn.get"),
            "credential-id",
            b"public-key-bytes",
            5,
        )
        assert ok is False and count == 5
        await session.flush()
        assert await _consumed_by_hash(session, _decode(pending)) is False

    _run(body)
