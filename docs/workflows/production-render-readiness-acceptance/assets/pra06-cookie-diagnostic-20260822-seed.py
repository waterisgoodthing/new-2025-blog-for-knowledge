#!/usr/bin/env python3
"""Prepare and disable the isolated synthetic M30 diagnostic fixture.

The prepare command prints the runtime password to stdout for the parent
process only. Callers must capture it in memory and must not log or persist it.
"""

from __future__ import annotations

import asyncio
import json
import secrets
import sys
from datetime import datetime, timezone

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.models.note import Note, User
from app.models.session import AdminSession
from app.utils.auth import hash_password


USERNAME = sys.argv[2] if len(sys.argv) > 2 else "pra06-cookie-diagnostic-admin"


async def prepare() -> None:
    from app.config import get_settings

    settings = get_settings()
    engine = create_async_engine(settings.DATABASE_URL)
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    password = secrets.token_urlsafe(32)
    try:
        async with session_factory() as session:
            await session.execute(delete(AdminSession))
            await session.execute(delete(Note))
            existing = await session.scalar(select(User).where(User.username == USERNAME))
            if existing is not None:
                await session.delete(existing)
                await session.flush()

            now = datetime.now(timezone.utc).replace(tzinfo=None)
            notes: list[Note] = []
            for index in range(1, 31):
                if index <= 10:
                    note_type = "note"
                elif index <= 20:
                    note_type = "blog"
                else:
                    note_type = "mistake"
                if index <= 20:
                    status = "published"
                    hidden = False
                elif index <= 25:
                    status = "published"
                    hidden = True
                else:
                    status = "draft"
                    hidden = True
                slug = f"pra06-cookie-{index:02d}"
                if index == 1:
                    slug = "pra06-cookie-d1"
                notes.append(
                    Note(
                        slug=slug,
                        title=f"PRA-06 synthetic {index:02d}",
                        content=(
                            "# Synthetic diagnostic note\n\n"
                            "This content is isolated and deterministic.\n"
                            "\n- item one\n- item two\n"
                        ),
                        type=note_type,
                        status=status,
                        hidden=hidden,
                        summary="Synthetic PRA-06 diagnostic content",
                        created_at=now,
                        updated_at=now,
                    )
                )
            session.add_all(notes)
            session.add(User(username=USERNAME, password_hash=hash_password(password), is_admin=True))
            await session.commit()
    finally:
        await engine.dispose()

    print(
        json.dumps(
            {
                "username": USERNAME,
                "password": password,
                "fixture": {
                    "total": 30,
                    "public_visible": 20,
                    "published_hidden": 5,
                    "drafts": 5,
                    "d1_public": True,
                    "types": {"note": 10, "blog": 10, "mistake": 10},
                },
            }
        )
    )


async def disable() -> None:
    from app.config import get_settings

    settings = get_settings()
    engine = create_async_engine(settings.DATABASE_URL)
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    try:
        async with session_factory() as session:
            user = await session.scalar(select(User).where(User.username == USERNAME))
            if user is not None:
                await session.execute(
                    update(AdminSession)
                    .where(AdminSession.user_id == user.id)
                    .values(revoked=True)
                )
                user.password_hash = "disabled"
                user.is_admin = False
                await session.commit()
    finally:
        await engine.dispose()
    print(json.dumps({"username": USERNAME, "disabled": True}))


if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] not in {"prepare", "disable"}:
        raise SystemExit("usage: seed.py prepare|disable [username]")
    asyncio.run(prepare() if sys.argv[1] == "prepare" else disable())
