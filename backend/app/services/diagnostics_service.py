import os
from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.diagnostics import (
    DiagnosticCheck,
    DiagnosticChecks,
    DiagnosticsResponse,
)


async def get_diagnostics(
    session: AsyncSession,
    *,
    upload_root: Path,
    auth_bypass_active: bool,
) -> DiagnosticsResponse:
    try:
        await session.execute(text("SELECT 1"))
        database_status = "ok"
    except Exception:
        database_status = "error"

    try:
        storage_status = (
            "ok"
            if upload_root.is_dir()
            and os.access(upload_root, os.R_OK | os.W_OK)
            else "error"
        )
    except OSError:
        storage_status = "unknown"

    auth_status = "warning" if auth_bypass_active else "ok"
    statuses = (database_status, storage_status, auth_status)

    return DiagnosticsResponse(
        generated_at=datetime.now(timezone.utc),
        overall="ok" if all(status == "ok" for status in statuses) else "degraded",
        checks=DiagnosticChecks(
            service=DiagnosticCheck(status="ok"),
            database=DiagnosticCheck(status=database_status),
            storage=DiagnosticCheck(status=storage_status),
            auth=DiagnosticCheck(status=auth_status),
        ),
    )
