from pathlib import Path


MIGRATION = Path(__file__).parents[1] / "alembic" / "versions" / "027_guestbook.py"


def _source() -> str:
    return MIGRATION.read_text(encoding="utf-8")


def test_027_is_a_single_linked_revision() -> None:
    source = _source()
    assert 'revision: str = "027"' in source
    assert 'down_revision: str | None = "026"' in source


def test_guestbook_ddl_matches_the_current_models() -> None:
    source = _source()
    for token in (
        '"guest_messages"',
        '"guest_message_bans"',
        '"content", sa.Text(), nullable=False',
        '"nickname", sa.String(length=100)',
        '"attachment_type", sa.String(length=20)',
        '"attachment_slug", sa.String(length=255)',
        '"ip_address", sa.String(length=45)',
        '"user_agent", sa.Text()',
        '"status", sa.String(length=20), nullable=False, server_default="visible"',
        '"created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")',
        '"idx_guest_messages_status"',
        '"idx_guest_messages_attachment"',
        '"idx_guest_messages_created"',
        '"ix_guest_message_bans_ip_address"',
    ):
        assert token in source


def test_upgrade_fails_closed_for_partial_or_incompatible_existing_schema() -> None:
    source = _source()
    assert "_assert_guest_schema_compatible" in source
    assert "Both guest tables must exist together" in source
    assert "Guest table is incompatible" in source
    assert "set(actual_indexes) != set(expected_indexes[table_name])" in source
    assert "get_unique_constraints" in source
    assert "get_foreign_keys" in source
    assert "get_check_constraints" in source
    assert "pg_get_serial_sequence" in source
    assert "raise RuntimeError" in source
    assert "CREATE TABLE IF NOT EXISTS" not in source


def test_downgrade_drops_only_exactly_owned_tables() -> None:
    source = _source()
    assert 'OWNERSHIP_MARKER = "pr04:guest-schema:027:owned"' in source
    assert "_owned_guest_tables" in source
    assert "COMMENT ON TABLE" in source
    assert "marker_literal = OWNERSHIP_MARKER.replace" in source
    assert 'op.drop_table("guest_message_bans", schema="public")' in source
    assert 'op.drop_table("guest_messages", schema="public")' in source
    assert "CASCADE" not in source
    assert "raise RuntimeError" in source
