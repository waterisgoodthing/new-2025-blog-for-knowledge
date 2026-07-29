"""add markdown versions, wikilinks and search support

Revision ID: 024
Revises: 023
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "024"
down_revision: str | None = "023"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("notes", sa.Column("revision", sa.Integer(), server_default="1", nullable=True))
    op.execute("UPDATE notes SET revision = 1 WHERE revision IS NULL")
    op.alter_column("notes", "revision", nullable=False)
    op.create_table(
        "note_versions",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("note_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["note_id"], ["notes.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("note_id", "version", name="uq_note_versions_note_version"),
    )
    op.create_index("idx_note_versions_note_created", "note_versions", ["note_id", "created_at"])
    op.create_table(
        "note_links",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("source_note_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("target_note_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("target_slug", sa.String(255), nullable=False),
        sa.Column("raw_link", sa.String(255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["source_note_id"], ["notes.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["target_note_id"], ["notes.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("source_note_id", "raw_link", name="uq_note_links_source_raw"),
    )
    op.create_index("idx_note_links_target", "note_links", ["target_note_id"])
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")


def downgrade() -> None:
    op.execute("DROP EXTENSION IF EXISTS pg_trgm")
    op.drop_index("idx_note_links_target", table_name="note_links")
    op.drop_table("note_links")
    op.drop_index("idx_note_versions_note_created", table_name="note_versions")
    op.drop_table("note_versions")
    op.drop_column("notes", "revision")
