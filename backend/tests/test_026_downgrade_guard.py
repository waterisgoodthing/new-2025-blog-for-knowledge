from pathlib import Path

MIGRATION = Path(__file__).parents[1] / "alembic" / "versions" / "026_legacy_system_retirement.py"


def test_026_declares_an_explicit_guarded_downgrade() -> None:
    source = MIGRATION.read_text(encoding="utf-8")
    assert "def downgrade() -> None:" in source
    assert "raise RuntimeError" in source
    assert "intentionally irreversible" in source


def test_026_migration_source_compiles() -> None:
    compile(MIGRATION.read_text(encoding="utf-8"), str(MIGRATION), "exec")
