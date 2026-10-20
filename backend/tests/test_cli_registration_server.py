"""W4-F02 regression: the CLI registration server keeps one event loop for DB work.

Starts the real HTTP server from ``app.cli`` against the scratch database and
issues two consecutive ``GET /api/passkey/register/options`` requests. Before the
fix each request created and closed its own event loop, so the second request
reused an asyncpg pooled connection bound to a closed loop and failed with
``InterfaceError: another operation is in progress``.

Run against the scratch database supplied through ``DATABASE_URL``.
"""

from __future__ import annotations

import asyncio
import json
import os
import threading
import urllib.request

import pytest
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from app.cli import create_registration_server
from app.models.webauthn_challenge import WebAuthnChallenge

DATABASE_URL = os.environ.get("DATABASE_URL")

pytestmark = pytest.mark.skipif(
    not DATABASE_URL, reason="requires scratch astra_week4_* DATABASE_URL"
)


def _clear_challenges() -> None:
    async def _main():
        engine = create_async_engine(DATABASE_URL)
        try:
            async with AsyncSession(engine, expire_on_commit=False) as session:
                await session.execute(delete(WebAuthnChallenge))
                await session.commit()
        finally:
            await engine.dispose()

    asyncio.run(_main())


def _count_challenges() -> int:
    async def _main():
        engine = create_async_engine(DATABASE_URL)
        try:
            async with AsyncSession(engine, expire_on_commit=False) as session:
                rows = (await session.execute(select(WebAuthnChallenge))).scalars().all()
                return len(rows)
        finally:
            await engine.dispose()

    return asyncio.run(_main())


def _fetch_options(port: int) -> tuple[int, dict]:
    with urllib.request.urlopen(
        f"http://localhost:{port}/api/passkey/register/options", timeout=15
    ) as response:
        return response.status, json.loads(response.read())


def test_two_consecutive_options_requests_both_succeed():
    _clear_challenges()
    server = create_registration_server(0, "localhost", DATABASE_URL)
    port = server.server_address[1]
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        first_status, first_body = _fetch_options(port)
        second_status, second_body = _fetch_options(port)

        assert first_status == 200
        assert second_status == 200
        assert first_body["publicKey"]["challenge"]
        assert second_body["publicKey"]["challenge"]
        assert first_body["publicKey"]["challenge"] != second_body["publicKey"]["challenge"]
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)
        _clear_challenges()


def test_two_consecutive_options_requests_persist_one_challenge_each():
    _clear_challenges()
    server = create_registration_server(0, "localhost", DATABASE_URL)
    port = server.server_address[1]
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        _fetch_options(port)
        _fetch_options(port)
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)

    try:
        assert _count_challenges() == 2
    finally:
        _clear_challenges()
