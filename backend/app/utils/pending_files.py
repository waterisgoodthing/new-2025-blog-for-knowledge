"""Request-scoped bookkeeping for filesystem writes.

Attachment bytes are moved into place *before* the surrounding DB transaction
commits. If that transaction later fails -- the final ``commit`` in ``get_db``
can fail even after a successful ``flush`` -- the DB row is rolled back but the
already-written file would be orphaned. Callers therefore record each written
path on the session, and the request teardown discards those files on failure.

Only paths explicitly tracked here are ever removed, which bounds the cleanup
to the failing request and never touches committed attachments.
"""
from __future__ import annotations

from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession

_PENDING_KEY = "pending_files"


def track_pending_file(session: AsyncSession, path: Path | str) -> None:
    session.info.setdefault(_PENDING_KEY, set()).add(str(path))


def clear_pending_files(session: AsyncSession) -> None:
    session.info.pop(_PENDING_KEY, None)


async def discard_pending_files(session: AsyncSession) -> None:
    for raw in session.info.pop(_PENDING_KEY, set()):
        try:
            Path(raw).unlink()
        except FileNotFoundError:
            pass
        except OSError:
            # Never let cleanup mask the original failure.
            pass
