#!/usr/bin/env python3
"""PR-12 verify: migration 032 matrix (fresh/upgrade/downgrade/constraints/cascade).

Run exclusively through the Week 3 scratch guard against a FRESH scratch DB:

    python3 scripts/week3-scratch-guard.py run \\
        --db-name astra_week3_pr12_mig \\
        -- backend/.venv/bin/python scripts/pr12_verify_migration_matrix.py

Writes logs to docs/workflows/personal-learning-system-convergence/week3/evidence/migrations/.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from sqlalchemy import create_engine, text

ROOT = Path(__file__).resolve().parent.parent
BACKEND = ROOT / "backend"
EVIDENCE = ROOT / "docs/workflows/personal-learning-system-convergence/week3/evidence/migrations"

FAILURES: list[str] = []


def log(name: str, body: str) -> Path:
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    path = EVIDENCE / f"pr-12-{name}"
    path.write_text(body, encoding="utf-8")
    print(f"WROTE {path.relative_to(ROOT)}")
    return path


def check(condition: bool, label: str, detail: str = "") -> bool:
    mark = "PASS" if condition else "FAIL"
    line = f"{mark}: {label}" + (f" | {detail}" if detail else "")
    print(line)
    if not condition:
        FAILURES.append(line)
    return condition


def sync_engine():
    url = os.environ["DATABASE_URL"].replace(
        "postgresql+asyncpg://", "postgresql+psycopg2://"
    )
    return create_engine(url, isolation_level="AUTOCOMMIT")


def run_alembic(*args: str) -> subprocess.CompletedProcess:
    env = dict(os.environ)
    existing = env.get("PYTHONPATH")
    env["PYTHONPATH"] = str(BACKEND) + (os.pathsep + existing if existing else "")
    return subprocess.run(
        [str(BACKEND / ".venv/bin/alembic"), *args],
        cwd=str(BACKEND),
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )


def column_rows(engine) -> list[tuple[str, str, str, str]]:
    with engine.connect() as conn:
        rows = conn.execute(
            text(
                "SELECT column_name, data_type, udt_name, is_nullable "
                "FROM information_schema.columns "
                "WHERE table_schema='public' AND table_name='note_knowledge_points' "
                "ORDER BY ordinal_position"
            )
        ).fetchall()
    return [(r[0], r[1], r[2], r[3]) for r in rows]


def primary_key_columns(engine) -> list[str]:
    with engine.connect() as conn:
        rows = conn.execute(
            text(
                "SELECT a.attname FROM pg_index i "
                "JOIN pg_attribute a ON a.attrelid = i.indrelid AND a.attnum = ANY(i.indkey) "
                "WHERE i.indrelid = 'public.note_knowledge_points'::regclass AND i.indisprimary "
                "ORDER BY a.attnum"
            )
        ).fetchall()
    return [r[0] for r in rows]


def foreign_keys(engine) -> dict[str, tuple[str, str]]:
    with engine.connect() as conn:
        rows = conn.execute(
            text(
                "SELECT conname, confdeltype, confrelid::regclass::text "
                "FROM pg_constraint "
                "WHERE conrelid = 'public.note_knowledge_points'::regclass AND contype = 'f'"
            )
        ).fetchall()
    return {r[0]: (r[1], r[2]) for r in rows}


def index_names(engine) -> set[str]:
    with engine.connect() as conn:
        rows = conn.execute(
            text(
                "SELECT indexname FROM pg_indexes "
                "WHERE schemaname='public' AND tablename='note_knowledge_points'"
            )
        ).fetchall()
    return {r[0] for r in rows}


def table_names(engine) -> set[str]:
    with engine.connect() as conn:
        rows = conn.execute(
            text(
                "SELECT tablename FROM pg_tables WHERE schemaname='public'"
            )
        ).fetchall()
    return {r[0] for r in rows}


def main() -> int:
    url = os.environ.get("DATABASE_URL", "")
    if "astra_week3_pr12" not in url:
        print("FAIL: must run via week3-scratch-guard with an astra_week3_pr12* database")
        return 2

    try:
        import psycopg2  # noqa: F401
    except ImportError:
        subprocess.run(
            [str(BACKEND / ".venv/bin/pip"), "install", "-q", "psycopg2-binary"],
            check=False,
        )

    engine = sync_engine()
    report: list[str] = []

    # ------------------------------------------------------------------
    # A. fresh DB guard + fresh -> 032
    # ------------------------------------------------------------------
    pre_tables = table_names(engine)
    check(
        "note_knowledge_points" not in pre_tables,
        "scratch DB starts without note_knowledge_points (fresh)",
        str(sorted(t for t in pre_tables if t.startswith("note"))),
    )

    current0 = run_alembic("current")
    report.append("== A. live alembic current (pre-upgrade) ==")
    report.append(current0.stdout + current0.stderr)

    up = run_alembic("upgrade", "head")
    report.append("== B. fresh upgrade head ==")
    report.append(up.stdout + up.stderr)
    check(up.returncode == 0, "fresh upgrade head exits 0", up.stderr[-400:])
    check("032" in up.stdout + up.stderr, "fresh upgrade applies 032")

    current = run_alembic("current")
    report.append("== B2. alembic current ==")
    report.append(current.stdout)
    check("032" in current.stdout, "alembic current == 032", current.stdout.strip())

    heads = run_alembic("heads")
    report.append("== B3. alembic heads ==")
    report.append(heads.stdout)
    head_lines = [ln for ln in heads.stdout.splitlines() if "(head)" in ln]
    check(
        len(head_lines) == 1 and head_lines[0].startswith("032"),
        "single head == 032",
        heads.stdout.strip(),
    )
    log("heads.log", heads.stdout + current.stdout + "\n")
    log("fresh-032.log", up.stdout + up.stderr + "\n")

    # ------------------------------------------------------------------
    # C. schema shape
    # ------------------------------------------------------------------
    report.append("== C. schema shape at 032 ==")
    cols = {row[0]: row for row in column_rows(engine)}
    report.append(f"columns={cols}")
    check(set(cols) == {"note_id", "knowledge_point_id", "created_at"}, "three columns", str(list(cols)))
    check(cols.get("note_id", ("", "", "", ""))[2] == "uuid", "note_id is uuid", str(cols.get("note_id")))
    check(
        cols.get("knowledge_point_id", ("", "", "", ""))[2] in {"int4", "int8"},
        "knowledge_point_id is integer",
        str(cols.get("knowledge_point_id")),
    )
    check(cols.get("created_at", ("", "", "", ""))[3] == "NO", "created_at is NOT NULL")

    pk = primary_key_columns(engine)
    check(pk == ["note_id", "knowledge_point_id"], "composite PK (note_id, knowledge_point_id)", str(pk))

    fks = foreign_keys(engine)
    report.append(f"foreign_keys={fks}")
    cascade_targets = {
        name: (deltype, target)
        for name, (deltype, target) in fks.items()
    }
    check(len(fks) == 2, "exactly two foreign keys", str(list(fks)))
    check(
        all(deltype == "c" for deltype, _ in fks.values()),
        "both foreign keys ON DELETE CASCADE",
        str(cascade_targets),
    )
    referenced = {target for _, target in fks.values()}
    check(
        referenced == {"notes", "knowledge_points"},
        "FKs reference notes and knowledge_points",
        str(referenced),
    )

    indexes = index_names(engine)
    report.append(f"indexes={sorted(indexes)}")
    check("idx_note_knowledge_points_kp" in indexes, "idx_note_knowledge_points_kp exists")
    check("note_knowledge_points_pkey" in indexes, "primary key index exists")
    log("schema-shape.log", "\n".join(str(x) for x in [cols, pk, fks, sorted(indexes)]) + "\n")

    # ------------------------------------------------------------------
    # D. duplicate rejection + cascade
    # ------------------------------------------------------------------
    report.append("== D. duplicate + cascade ==")
    with engine.begin() as conn:
        conn.execute(text("DELETE FROM public.note_knowledge_points"))
        conn.execute(text("DELETE FROM public.notes WHERE slug = 'pr12-mig-note'"))
        conn.execute(text("DELETE FROM public.knowledge_points WHERE name = 'pr12-mig-kp'"))
        conn.execute(text("DELETE FROM public.subjects WHERE name = 'pr12-mig-subject'"))
        subject_id = conn.execute(
            text("INSERT INTO public.subjects (name) VALUES ('pr12-mig-subject') RETURNING id")
        ).scalar_one()
        kp_id = conn.execute(
            text(
                "INSERT INTO public.knowledge_points (subject_id, name) "
                "VALUES (:s, 'pr12-mig-kp') RETURNING id"
            ),
            {"s": subject_id},
        ).scalar_one()
        note_id = conn.execute(
            text(
                "INSERT INTO public.notes "
                "(id,slug,title,content,type,ef,interval,repetitions) "
                "VALUES (gen_random_uuid(),'pr12-mig-note','t','c','note',2.5,0,0) "
                "RETURNING id"
            )
        ).scalar_one()
        conn.execute(
            text(
                "INSERT INTO public.note_knowledge_points (note_id, knowledge_point_id) "
                "VALUES (:n, :k)"
            ),
            {"n": note_id, "k": kp_id},
        )

    duplicate_rejected = False
    try:
        with engine.begin() as conn:
            conn.execute(
                text(
                    "INSERT INTO public.note_knowledge_points (note_id, knowledge_point_id) "
                    "VALUES (:n, :k)"
                ),
                {"n": note_id, "k": kp_id},
            )
    except Exception as exc:  # noqa: BLE001
        duplicate_rejected = "unique" in str(exc).lower() or "duplicate" in str(exc).lower()
        report.append(f"duplicate insert rejected: {type(exc).__name__}: {exc}")
    check(duplicate_rejected, "duplicate (note_id, knowledge_point_id) rejected")

    with engine.begin() as conn:
        remaining = conn.execute(
            text("SELECT count(*) FROM public.note_knowledge_points WHERE note_id = :n"),
            {"n": note_id},
        ).scalar_one()
    check(remaining == 1, "exactly one link row before cascade", str(remaining))

    with engine.begin() as conn:
        conn.execute(text("DELETE FROM public.notes WHERE id = :n"), {"n": note_id})
    with engine.connect() as conn:
        after_note_delete = conn.execute(
            text("SELECT count(*) FROM public.note_knowledge_points WHERE note_id = :n"),
            {"n": note_id},
        ).scalar_one()
    check(after_note_delete == 0, "deleting note cascades link rows", str(after_note_delete))

    with engine.begin() as conn:
        second_note_id = conn.execute(
            text(
                "INSERT INTO public.notes "
                "(id,slug,title,content,type,ef,interval,repetitions) "
                "VALUES (gen_random_uuid(),'pr12-mig-note-2','t','c','note',2.5,0,0) "
                "RETURNING id"
            )
        ).scalar_one()
        conn.execute(
            text(
                "INSERT INTO public.note_knowledge_points (note_id, knowledge_point_id) "
                "VALUES (:n, :k)"
            ),
            {"n": second_note_id, "k": kp_id},
        )
        conn.execute(text("DELETE FROM public.knowledge_points WHERE id = :k"), {"k": kp_id})
    with engine.connect() as conn:
        after_kp_delete = conn.execute(
            text("SELECT count(*) FROM public.note_knowledge_points WHERE knowledge_point_id = :k"),
            {"k": kp_id},
        ).scalar_one()
    check(after_kp_delete == 0, "deleting knowledge point cascades link rows", str(after_kp_delete))

    # ------------------------------------------------------------------
    # E. downgrade 032 -> 031, then re-upgrade
    # ------------------------------------------------------------------
    down = run_alembic("downgrade", "031")
    report.append("== E. downgrade to 031 ==")
    report.append(down.stdout + down.stderr)
    check(down.returncode == 0, "downgrade to 031 exits 0", down.stderr[-400:])
    check("note_knowledge_points" not in table_names(engine), "table dropped at 031")
    current_031 = run_alembic("current")
    check("031" in current_031.stdout, "alembic current == 031 after downgrade", current_031.stdout.strip())

    up_again = run_alembic("upgrade", "head")
    report.append("== E2. re-upgrade 031 -> 032 ==")
    report.append(up_again.stdout + up_again.stderr)
    check(up_again.returncode == 0, "re-upgrade to 032 exits 0", up_again.stderr[-400:])
    check("note_knowledge_points" in table_names(engine), "table re-created by re-upgrade")
    check("idx_note_knowledge_points_kp" in index_names(engine), "index re-created by re-upgrade")
    log("downgrade-reupgrade.log", down.stdout + down.stderr + up_again.stdout + up_again.stderr + "\n")

    # ------------------------------------------------------------------
    # F. polymorphic knowledge_point_links untouched
    # ------------------------------------------------------------------
    with engine.connect() as conn:
        links_columns = {
            row[0]
            for row in conn.execute(
                text(
                    "SELECT column_name FROM information_schema.columns "
                    "WHERE table_schema='public' AND table_name='knowledge_point_links'"
                )
            ).fetchall()
        }
    report.append(f"knowledge_point_links columns={sorted(links_columns)}")
    check(
        {"id", "knowledge_point_id", "target_type", "target_id", "created_at"}
        <= links_columns,
        "knowledge_point_links unchanged",
        str(sorted(links_columns)),
    )

    log("migration-matrix.log", "\n".join(report) + "\n")
    summary = "ALL_PASS" if not FAILURES else f"FAILURES={len(FAILURES)}"
    log("summary.log", summary + "\n" + "\n".join(FAILURES) + "\n")
    print(f"MIGRATION_MATRIX_{summary}")
    return 0 if not FAILURES else 1


if __name__ == "__main__":
    sys.exit(main())
