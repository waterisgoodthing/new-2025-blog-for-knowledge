"""Provision the guestbook tables without taking ownership of legacy tables."""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect, text


revision: str = "027"
down_revision: str | None = "026"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

OWNERSHIP_MARKER = "pr04:guest-schema:027:owned"
_TABLES = ("guest_messages", "guest_message_bans")


def _table_exists(inspector, table_name: str) -> bool:
    return table_name in inspector.get_table_names(schema="public")


def _normalise_default(value: str | None) -> str | None:
    if value is None:
        return None
    return "".join(value.lower().split()).replace("current_timestamp", "now()")


def _assert_guest_schema_compatible(bind) -> None:
    inspector = inspect(bind)
    present = {table for table in _TABLES if _table_exists(inspector, table)}
    if present and present != set(_TABLES):
        raise RuntimeError("Both guest tables must exist together; refusing partial upgrade.")
    if not present:
        return

    expected_columns = {
        "guest_messages": {
            "id": ("uuid", None, False, None),
            "content": ("text", None, False, None),
            "nickname": ("character varying", 100, True, None),
            "attachment_type": ("character varying", 20, True, None),
            "attachment_slug": ("character varying", 255, True, None),
            "ip_address": ("character varying", 45, True, None),
            "user_agent": ("text", None, True, None),
            "status": ("character varying", 20, False, "'visible'::character varying"),
            "created_at": ("timestamp with time zone", None, False, "now()"),
        },
        "guest_message_bans": {
            "id": ("integer", None, False, "sequence"),
            "ip_address": ("character varying", 45, False, None),
            "reason": ("text", None, True, None),
            "expires_at": ("timestamp with time zone", None, True, None),
            "created_at": ("timestamp with time zone", None, False, "now()"),
        },
    }
    expected_indexes = {
        "guest_messages": {
            "idx_guest_messages_status": (False, ["status"]),
            "idx_guest_messages_attachment": (False, ["attachment_type", "attachment_slug"]),
            "idx_guest_messages_created": (False, ["created_at"]),
        },
        "guest_message_bans": {
            "ix_guest_message_bans_ip_address": (False, ["ip_address"]),
        },
    }

    for table_name, columns in expected_columns.items():
        actual = {column["name"]: column for column in inspector.get_columns(table_name, schema="public")}
        if set(actual) != set(columns):
            raise RuntimeError(f"Guest table is incompatible: {table_name} columns differ.")
        for name, (type_name, length, nullable, default) in columns.items():
            column = actual[name]
            actual_type = str(column["type"]).lower()
            if type_name == "character varying":
                compatible_type = actual_type == f"varchar({length})"
            elif type_name == "timestamp with time zone":
                compatible_type = actual_type in {"timestamp", "timestamp with time zone"} and getattr(column["type"], "timezone", False)
            else:
                compatible_type = actual_type == type_name
            actual_default = column.get("default")
            if default == "sequence":
                default_matches = actual_default is not None and "nextval(" in actual_default.lower()
            else:
                default_matches = _normalise_default(actual_default) == _normalise_default(default)
            if not compatible_type or column["nullable"] != nullable or not default_matches:
                raise RuntimeError(f"Guest table is incompatible: {table_name}.{name} differs.")
        if table_name == "guest_message_bans":
            sequence_name = bind.execute(
                text("SELECT pg_get_serial_sequence('public.guest_message_bans', 'id')")
            ).scalar_one_or_none()
            if sequence_name != "public.guest_message_bans_id_seq":
                raise RuntimeError("Guest table is incompatible: guest_message_bans.id sequence differs.")

        primary_key = inspector.get_pk_constraint(table_name, schema="public").get("constrained_columns")
        if primary_key != ["id"]:
            raise RuntimeError(f"Guest table is incompatible: {table_name} primary key differs.")

        actual_indexes = {
            index["name"]: (index["unique"], index["column_names"])
            for index in inspector.get_indexes(table_name, schema="public")
        }
        if set(actual_indexes) != set(expected_indexes[table_name]):
            raise RuntimeError(f"Guest table is incompatible: {table_name} indexes differ.")
        for index_name, expected in expected_indexes[table_name].items():
            if actual_indexes.get(index_name) != expected:
                raise RuntimeError(f"Guest table is incompatible: {table_name} indexes differ.")
        if inspector.get_unique_constraints(table_name, schema="public"):
            raise RuntimeError(f"Guest table is incompatible: {table_name} unique constraints differ.")
        if inspector.get_foreign_keys(table_name, schema="public"):
            raise RuntimeError(f"Guest table is incompatible: {table_name} foreign keys differ.")
        if inspector.get_check_constraints(table_name, schema="public"):
            raise RuntimeError(f"Guest table is incompatible: {table_name} check constraints differ.")


def _owned_guest_tables(bind) -> set[str]:
    rows = bind.execute(
        text(
            """
            SELECT c.relname, obj_description(c.oid, 'pg_class')
              FROM pg_class AS c
              JOIN pg_namespace AS n ON n.oid = c.relnamespace
             WHERE n.nspname = 'public' AND c.relname IN (:messages, :bans)
               AND c.relkind = 'r'
            """
        ),
        {"messages": _TABLES[0], "bans": _TABLES[1]},
    ).all()
    return {name for name, comment in rows if comment == OWNERSHIP_MARKER}


def upgrade() -> None:
    bind = op.get_bind()
    lock_key = 270027
    bind.execute(text("SELECT pg_advisory_xact_lock(:lock_key)"), {"lock_key": lock_key})
    _assert_guest_schema_compatible(bind)
    inspector = inspect(bind)
    if any(_table_exists(inspector, table) for table in _TABLES):
        return

    op.create_table(
        "guest_messages",
        sa.Column("id", sa.UUID(), primary_key=True, nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("nickname", sa.String(length=100)),
        sa.Column("attachment_type", sa.String(length=20)),
        sa.Column("attachment_slug", sa.String(length=255)),
        sa.Column("ip_address", sa.String(length=45)),
        sa.Column("user_agent", sa.Text()),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="visible"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        schema="public",
    )
    op.create_index("idx_guest_messages_status", "guest_messages", ["status"], schema="public")
    op.create_index(
        "idx_guest_messages_attachment",
        "guest_messages",
        ["attachment_type", "attachment_slug"],
        schema="public",
    )
    op.create_index("idx_guest_messages_created", "guest_messages", ["created_at"], schema="public")
    op.create_table(
        "guest_message_bans",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True, nullable=False),
        sa.Column("ip_address", sa.String(length=45), nullable=False),
        sa.Column("reason", sa.Text()),
        sa.Column("expires_at", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        schema="public",
    )
    op.create_index("ix_guest_message_bans_ip_address", "guest_message_bans", ["ip_address"], schema="public")
    marker_literal = OWNERSHIP_MARKER.replace("'", "''")
    bind.execute(text(f"COMMENT ON TABLE public.guest_messages IS '{marker_literal}'"))
    bind.execute(text(f"COMMENT ON TABLE public.guest_message_bans IS '{marker_literal}'"))


def downgrade() -> None:
    bind = op.get_bind()
    lock_key = 270027
    bind.execute(text("SELECT pg_advisory_xact_lock(:lock_key)"), {"lock_key": lock_key})
    inspector = inspect(bind)
    present = {table for table in _TABLES if _table_exists(inspector, table)}
    if not present:
        return
    if present != set(_TABLES):
        raise RuntimeError("Both guest tables must exist together; refusing partial downgrade.")
    owned = _owned_guest_tables(bind)
    if not owned:
        return
    if owned != set(_TABLES):
        raise RuntimeError("Guest table ownership markers are incomplete; refusing downgrade.")
    op.drop_table("guest_message_bans", schema="public")
    op.drop_table("guest_messages", schema="public")
