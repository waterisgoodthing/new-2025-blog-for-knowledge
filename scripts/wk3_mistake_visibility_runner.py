#!/usr/bin/env python3
"""CLI entry for the wk3-mistake-visibility-v1 ledger migration runner.

Every database-touching invocation must be launched through
``scripts/week3-scratch-guard.py run --db-name astra_week3_* -- ...``.

Usage:
    python scripts/wk3_mistake_visibility_runner.py --report-out /tmp/report.json
    python scripts/wk3_mistake_visibility_runner.py --report-out /tmp/report.json --dry-run
"""

from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="wk3-mistake-visibility-v1 runner")
    parser.add_argument("--report-out", required=True, help="Path for the JSON reconciliation report")
    parser.add_argument("--dry-run", action="store_true", help="Zero-persistence planning pass")
    return parser


async def _run(report_out: str, dry_run: bool) -> int:
    from app.database import async_session, engine
    from app.services.wk3_mistake_visibility_migration import (
        run_wk3_migration,
        write_report,
    )

    try:
        async with async_session() as session:
            report = await run_wk3_migration(session, dry_run=dry_run)
            if dry_run:
                await session.rollback()
            else:
                await session.commit()
        write_report(report, report_out)
        summary = report.to_json_dict()
        print(
            f"wk3-mistake-visibility-v1 dry_run={dry_run} "
            f"created={summary['targets']['created']} "
            f"reconciled={summary['targets']['visibility_reconciled']} "
            f"skipped={summary['targets']['skipped_already_migrated']} "
            f"rejected={len(summary['targets']['rejected'])} "
            f"replay_noop={summary['idempotency']['replay_noop']}"
        )
        return 0
    finally:
        await engine.dispose()


def main() -> int:
    args = build_parser().parse_args()
    return asyncio.run(_run(args.report_out, args.dry_run))


if __name__ == "__main__":
    raise SystemExit(main())
