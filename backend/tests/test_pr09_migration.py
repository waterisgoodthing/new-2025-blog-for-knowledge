"""PR-09 migration 031 tests: static shape + constraint semantics."""

from __future__ import annotations

import re
from pathlib import Path

import pytest

MIGRATION_PATH = Path(__file__).parents[1] / "alembic" / "versions" / "031_mistake_visibility_public.py"


def _migration_source() -> str:
    return MIGRATION_PATH.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# Static migration shape (no DB)
# ---------------------------------------------------------------------------


def test_migration_revision_and_down_revision() -> None:
    source = _migration_source()
    assert re.search(r'revision:\s*str\s*=\s*"031"', source)
    assert re.search(r'down_revision:\s*str\s*\|\s*None\s*=\s*"030"', source)


def test_migration_only_touches_ck_mistakes_visibility() -> None:
    source = _migration_source()
    fn_src = source.split("def upgrade")[1]
    assert "ck_mistakes_visibility" in fn_src
    assert "ck_questions_visibility" not in fn_src
    assert "ck_attachments_visibility" not in fn_src


def test_upgrade_widens_to_in_check() -> None:
    source = _migration_source()
    assert "visibility IN ('private','public')" in source


def test_downgrade_fail_closed_on_public_rows() -> None:
    source = _migration_source()
    assert "fail-closed" in source.lower()
    assert "visibility='public'" in source or "visibility = 'public'" in source
    assert "raise RuntimeError" in source


def test_downgrade_restores_private_only() -> None:
    source = _migration_source()
    assert "visibility = 'private'" in source


def test_upgrade_and_downgrade_use_transactional_alter() -> None:
    source = _migration_source()
    assert "pg_advisory_xact_lock" in source
    assert source.count("drop_constraint") >= 2
    assert source.count("create_check_constraint") >= 2


def test_model_check_matches_new_constraint() -> None:
    from app.models.mistake import Mistake

    checks = {
        c.name: str(c.sqltext)
        for c in Mistake.__table__.constraints
        if hasattr(c, "sqltext") and c.name
    }
    assert "ck_mistakes_visibility" in checks
    normalized = checks["ck_mistakes_visibility"].replace('"', "'").replace(" ", "")
    assert "IN('private','public')" in normalized


def test_revision_pin_in_main() -> None:
    import main

    assert main.EXPECTED_ALEMBIC_REVISION == "034"


def test_sibling_visibility_constraints_untouched_in_model() -> None:
    from app.models.attachment import Attachment
    from app.models.question import Question

    for model in (Question, Attachment):
        checks = {
            c.name: str(c.sqltext)
            for c in model.__table__.constraints
            if hasattr(c, "sqltext") and c.name and "visibility" in (c.name or "")
        }
        for name, sqltext in checks.items():
            assert name != "ck_mistakes_visibility"
            assert "public" not in sqltext.lower() or "private" in sqltext.lower()
