#!/usr/bin/env python3
"""PR-09 verify: migration 031 matrix (fresh/upgrade/downgrade/constraints/heads).

Run exclusively through the Week 3 scratch guard:

    python3 scripts/week3-scratch-guard.py run \\
        --db-name astra_week3_pr09_verify_mig \\
        --url postgresql+asyncpg://postgres@127.0.0.1:49621/astra_week3_pr09_verify_mig \\
        -- backend/.venv/bin/python scripts/pr09_verify_migration_matrix.py

Writes logs to docs/workflows/personal-learning-system-convergence/week3/evidence/migrations/.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import sqlalchemy
from sqlalchemy import create_engine, text

ROOT = Path(__file__).resolve().parent.parent
BACKEND = ROOT / "backend"
EVIDENCE = ROOT / "docs/workflows/personal-learning-system-convergence/week3/evidence/migrations"
SQL_EVIDENCE = ROOT / "docs/workflows/personal-learning-system-convergence/week3/evidence/sql"

FAILURES: list[str] = []


def log(name: str, body: str) -> Path:
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    path = EVIDENCE / f"pr-09-verify-{name}.log"
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


def psql_url() -> str:
    url = os.environ["DATABASE_URL"]
    return url.replace("postgresql+asyncpg://", "postgresql://").replace(
        "postgresql+psycopg2://", "postgresql://"
    )


def sync_engine():
    url = os.environ["DATABASE_URL"]
    return create_engine(url.replace("postgresql+asyncpg://", "postgresql+psycopg2://"), isolation_level="AUTOCOMMIT")


def run_alembic(*args: str) -> subprocess.CompletedProcess:
    env = dict(os.environ)
    return subprocess.run(
        [str(BACKEND / ".venv/bin/alembic"), *args],
        cwd=str(BACKEND),
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )


def constraint_shapes(engine) -> dict[str, str]:
    rows = engine.execute(text(
        "SELECT conname, pg_get_constraintdef(oid) AS def "
        "FROM pg_constraint "
        "WHERE conrelid = 'public.mistakes'::regclass OR conrelid='public.questions'::regclass "
        "OR conrelid='public.attachments'::regclass "
        "ORDER BY conname"
    )).fetchall()
    out = {}
    for name, definition in rows:
        if "visibility" in name:
            out[name] = definition
    return out


def main() -> int:
    url = os.environ.get("DATABASE_URL", "")
    if "astra_week3_pr09_" not in url:
        print("FAIL: must run via week3-scratch-guard with astra_week3_pr09_* database")
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
    # A. W3F-11 live alembic current pin (empty DB has no alembic_version yet)
    # ------------------------------------------------------------------
    current0 = run_alembic("current")
    report.append("== A. live alembic current (pre-upgrade) ==")
    report.append(current0.stdout)
    report.append(current0.stderr)

    # ------------------------------------------------------------------
    # B. fresh -> 031 full chain
    # ------------------------------------------------------------------
    up = run_alembic("upgrade", "head")
    report.append("== B. fresh upgrade head ==")
    report.append(up.stdout)
    report.append(up.stderr)
    check(up.returncode == 0, "fresh upgrade head exits 0")
    check("031" in up.stdout + up.stderr, "fresh upgrade applies 031")
    check("030" in up.stdout + up.stderr, "fresh upgrade chain includes 030")

    current = run_alembic("current")
    report.append("== B2. alembic current after upgrade ==")
    report.append(current.stdout)
    check("031" in current.stdout, "alembic current == 031")

    heads = run_alembic("heads")
    report.append("== B3. alembic heads ==")
    report.append(heads.stdout)
    check(heads.stdout.strip().splitlines()[0].startswith("031"), "single head starts with 031", heads.stdout.strip())
    check(len([ln for ln in heads.stdout.splitlines() if "(head)" in ln]) == 1, "exactly one head")

    shapes_after_031 = constraint_shapes(engine)
    report.append("== B4. constraint shapes at 031 ==")
    for name, definition in sorted(shapes_after_031.items()):
        report.append(f"{name} | {definition}")
    ck_mistakes = shapes_after_031.get("ck_mistakes_visibility", "")
    ck_questions = shapes_after_031.get("ck_questions_visibility", "")
    ck_attach = shapes_after_031.get("ck_attachments_visibility", "")
    check("private" in ck_mistakes and "public" in ck_mistakes, "ck_mistakes_visibility allows public+private", ck_mistakes)
    check("'private'" in ck_questions and "public" not in ck_questions.replace("private", ""), "ck_questions_visibility still private-only", ck_questions)
    check("'private'" in ck_attach and "public" not in ck_attach.replace("private", ""), "ck_attachments_visibility still private-only", ck_attach)

    # ------------------------------------------------------------------
    # C. constraint rejection / acceptance
    # ------------------------------------------------------------------
    report.append("== C. constraint checks ==")
    with engine.begin() as conn:
        conn.execute(text("DELETE FROM public.mistakes"))
        conn.execute(text("DELETE FROM public.notes WHERE type='mistake'"))
        conn.execute(text(
            "INSERT INTO public.notes (id,slug,title,content,type,ef,interval,repetitions) "
            "VALUES (gen_random_uuid(),'verify-mig-1','t','c','mistake',2.5,0,0)"
        ))
        note_id = conn.execute(text("SELECT id FROM public.notes WHERE slug='verify-mig-1'")).scalar_one()

    def insert_mistake(vis: str):
        with engine.begin() as conn:
            conn.execute(text(
                "INSERT INTO public.mistakes (id,source_draft_item_id,question_id,subject_id,title,question_text,"
                "my_answer,correct_answer,analysis,reason_category,mistake_reason,difficulty,status,visibility,version) "
                "VALUES (gen_random_uuid(), gen_random_uuid(), gen_random_uuid(), 1, 't','q','my','ca','an',"
                "'unknown',NULL,'easy','active',CAST(:v AS text),1)"
            ), {"v": vis})

    try:
        insert_mistake("x")
        check(False, "INSERT visibility='x' rejected")
        report.append("FAIL: visibility=x was accepted")
    except Exception as exc:  # noqa: BLE001
        check("IntegrityError" in type(exc).__name__ or "check" in str(exc).lower() or "violates" in str(exc).lower(),
              "INSERT visibility='x' rejected", type(exc).__name__)
        report.append(f"visibility=x rejected: {type(exc).__name__}: {exc}")

    for vis in ("private", "public"):
        try:
            insert_mistake(vis)
            check(True, f"INSERT visibility='{vis}' accepted")
            report.append(f"visibility={vis} accepted")
        except Exception as exc:  # noqa: BLE001
            check(False, f"INSERT visibility='{vis}' accepted", str(exc))
            report.append(f"visibility={vis} REJECTED: {exc}")

    log("constraints", "\n".join(report[-12:]) + "\n")

    # ------------------------------------------------------------------
    # D. downgrade fail-closed while public rows exist
    # ------------------------------------------------------------------
    with engine.connect() as conn:
        public_count = conn.execute(text("SELECT count(*) FROM public.mistakes WHERE visibility='public'")).scalar()
    check(int(public_count) > 0, "public rows present before downgrade attempt", str(public_count))

    down_fail = run_alembic("downgrade", "030")
    report.append("== D. downgrade 030 with public rows ==")
    report.append(down_fail.stdout)
    report.append(down_fail.stderr)
    combined = down_fail.stdout + down_fail.stderr
    check(down_fail.returncode != 0, "downgrade fails while public rows exist")
    check("fail-closed" in combined.lower(), "downgrade error says fail-closed", combined[-400:])
    check("visibility='public'" in combined or 'visibility="public"' in combined or "visibility = 'public'" in combined or "public" in combined,
          "downgrade error mentions public rows")

    current_after_fail = run_alembic("current")
    check("031" in current_after_fail.stdout, "version still 031 after failed downgrade", current_after_fail.stdout)
    shapes_still = constraint_shapes(engine)
    check("public" in shapes_still.get("ck_mistakes_visibility", ""), "constraint still widened after failed downgrade")
    log("downgrade-fail-closed", "\n".join([
        f"public_rows={public_count}",
        f"returncode={down_fail.returncode}",
        down_fail.stdout,
        down_fail.stderr,
        f"current={current_after_fail.stdout}",
        f"ck_mistakes_visibility={shapes_still.get('ck_mistakes_visibility')}",
    ]) + "\n")

    # ------------------------------------------------------------------
    # E. clear public rows -> downgrade 030 -> upgrade 031
    # ------------------------------------------------------------------
    with engine.begin() as conn:
        conn.execute(text("UPDATE public.mistakes SET visibility='private' WHERE visibility='public'"))
        conn.execute(text("DELETE FROM public.mistakes"))
    down_ok = run_alembic("downgrade", "030")
    report.append("== E. downgrade after clearing public rows ==")
    report.append(down_ok.stdout)
    report.append(down_ok.stderr)
    check(down_ok.returncode == 0, "downgrade 030 succeeds with zero public rows")
    shapes_at_030 = constraint_shapes(engine)
    ck_030 = shapes_at_030.get("ck_mistakes_visibility", "")
    check("'private'" in ck_030 and "public" not in ck_030.replace("'private'", ""), "030 constraint is private-only", ck_030)

    up_again = run_alembic("upgrade", "head")
    report.append("== E2. re-upgrade 030 -> 031 ==")
    report.append(up_again.stdout)
    report.append(up_again.stderr)
    check(up_again.returncode == 0, "re-upgrade to 031 succeeds")
    shapes_again = constraint_shapes(engine)
    check("public" in shapes_again.get("ck_mistakes_visibility", ""), "constraint widened again")

    # sibling constraints must be byte-identical across 030/031
    for name in ("ck_questions_visibility", "ck_attachments_visibility"):
        same = shapes_at_030.get(name) == shapes_again.get(name) == shapes_after_031.get(name)
        check(same, f"{name} unchanged across 030/031", str(shapes_at_030.get(name)))

    SQL_EVIDENCE.mkdir(parents=True, exist_ok=True)
    (SQL_EVIDENCE / "pr-09-verify-constraint-shapes-compare.txt").write_text(
        "\n".join([
            "at_030:",
            *[f"  {k} | {v}" for k, v in sorted(shapes_at_030.items())],
            "at_031:",
            *[f"  {k} | {v}" for k, v in sorted(shapes_after_031.items())],
            "after_reupgrade:",
            *[f"  {k} | {v}" for k, v in sorted(shapes_again.items())],
        ]) + "\n",
        encoding="utf-8",
    )

    log("migration-matrix", "\n".join(report) + "\n")
    log("heads", heads.stdout + current_after_fail.stdout + "\n")
    log("upgrade-fresh-031", up.stdout + up.stderr + "\n")
    log("upgrade-030-031", up_again.stdout + up_again.stderr + "\n")
    log("downgrade-clean-reupgrade", down_ok.stdout + down_ok.stderr + up_again.stdout + up_again.stderr + "\n")

    summary = "ALL_PASS" if not FAILURES else f"FAILURES={len(FAILURES)}"
    log("summary", summary + "\n" + "\n".join(FAILURES) + "\n")
    print(f"MIGRATION_MATRIX_{summary}")
    return 0 if not FAILURES else 1


if __name__ == "__main__":
    sys.exit(main())
