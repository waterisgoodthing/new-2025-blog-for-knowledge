"""Canonical Note <-> KnowledgePoint relation table (W3-D04 / PR-12).

Net-new ``note_knowledge_points`` association table:
  * ``note_id``            UUID    FK -> notes.id            ON DELETE CASCADE
  * ``knowledge_point_id`` INTEGER FK -> knowledge_points.id ON DELETE CASCADE
  * composite primary key ``(note_id, knowledge_point_id)`` (the required
    uniqueness for the pair)
  * ``idx_note_knowledge_points_kp`` covers the KP -> note lookup direction;
    the composite primary key already covers note -> KP.

The existing polymorphic ``knowledge_point_links`` table is intentionally left
untouched.

Revision ID: 032
Revises: 031
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect, text
from sqlalchemy.dialects import postgresql


revision: str = "032"
down_revision: str | None = "031"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

TABLE = "note_knowledge_points"
INDEX = "idx_note_knowledge_points_kp"
LOCK_KEY = 320032


def _table_exists(inspector, table_name: str) -> bool:
    return table_name in inspector.get_table_names(schema="public")


def _assert_prerequisites(bind) -> None:
    inspector = inspect(bind)
    for required in ("notes", "knowledge_points"):
        if not _table_exists(inspector, required):
            raise RuntimeError(
                f"{required} table is missing; refusing unsafe alteration"
            )


def upgrade() -> None:
    bind = op.get_bind()
    bind.execute(text("SELECT pg_advisory_xact_lock(:lock_key)"), {"lock_key": LOCK_KEY})

    _assert_prerequisites(bind)
    inspector = inspect(bind)
    if _table_exists(inspector, TABLE):
        raise RuntimeError(
            f"{TABLE} already exists; expected pre-032 shape"
        )

    op.create_table(
        TABLE,
        sa.Column("note_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("knowledge_point_id", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.ForeignKeyConstraint(
            ["note_id"],
            ["notes.id"],
            name="fk_note_knowledge_points_note_id",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["knowledge_point_id"],
            ["knowledge_points.id"],
            name="fk_note_knowledge_points_knowledge_point_id",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("note_id", "knowledge_point_id"),
        schema="public",
    )
    op.create_index(
        INDEX,
        TABLE,
        ["knowledge_point_id", "note_id"],
        unique=False,
        schema="public",
    )


def downgrade() -> None:
    bind = op.get_bind()
    bind.execute(text("SELECT pg_advisory_xact_lock(:lock_key)"), {"lock_key": LOCK_KEY})

    inspector = inspect(bind)
    if not _table_exists(inspector, TABLE):
        raise RuntimeError(f"{TABLE} is missing; expected 032 shape")

    op.drop_index(INDEX, table_name=TABLE, schema="public")
    op.drop_table(TABLE, schema="public")
