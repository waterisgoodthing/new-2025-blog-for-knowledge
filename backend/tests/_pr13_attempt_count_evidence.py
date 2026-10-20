"""PR-13 read-only evidence: daily practice never creates an Attempt.

Runnable (not a pytest test) so the count is measured on a committed-eligible
session and printed for the evidence ledger:

    python3 scripts/week3-scratch-guard.py run --db-name astra_week3_pr13 \
        -- backend/.venv/bin/python tests/_pr13_attempt_count_evidence.py
"""

from __future__ import annotations

import asyncio
import json

from sqlalchemy import func, select

from app.utils.scratch_db_safety import require_scratch_database
from app.config import get_settings

require_scratch_database(get_settings().DATABASE_URL)

from app.database import async_session, engine
from app.models.attempt import Attempt
from app.services import practice_service


async def _count(session) -> int:
    return int((await session.execute(select(func.count()).select_from(Attempt))).scalar_one())


async def main() -> None:
    await engine.dispose(close=False)
    async with async_session() as session:
        before = await _count(session)
        first = await practice_service.get_daily_practice(session)
        second = await practice_service.get_daily_practice(session)
        after = await _count(session)
        await session.rollback()
    await engine.dispose()
    print(
        json.dumps(
            {
                "attempts_before": before,
                "attempts_after": after,
                "unchanged": before == after,
                "first_returned_count": first.empty_metadata.returned_count,
                "second_returned_count": second.empty_metadata.returned_count,
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    asyncio.run(main())
