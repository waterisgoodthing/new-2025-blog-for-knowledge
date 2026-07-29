"""align subject knowledge tree

Revision ID: 019
Revises: 018
Create Date: 2026-07-15
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "019"
down_revision: str | None = "018"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if "chapters" in inspector.get_table_names():
        chapter_count = bind.execute(sa.text("SELECT count(*) FROM chapters")).scalar_one()
        if chapter_count:
            raise RuntimeError(
                "Cannot drop non-empty chapters table without an approved conversion plan"
            )

    op.add_column(
        "subjects",
        sa.Column("status", sa.String(20), nullable=False, server_default="active"),
    )
    op.execute(
        "UPDATE subjects SET status = CASE WHEN is_active THEN 'active' ELSE 'archived' END"
    )
    op.create_check_constraint(
        "ck_subjects_status",
        "subjects",
        "status IN ('active', 'archived')",
    )
    op.drop_column("subjects", "is_active")

    op.add_column("knowledge_points", sa.Column("parent_id", sa.Integer(), nullable=True))
    op.add_column(
        "knowledge_points",
        sa.Column("status", sa.String(20), nullable=False, server_default="active"),
    )
    op.execute(
        "UPDATE knowledge_points "
        "SET status = CASE WHEN is_active THEN 'active' ELSE 'archived' END"
    )
    op.create_check_constraint(
        "ck_knowledge_points_status",
        "knowledge_points",
        "status IN ('active', 'archived')",
    )
    op.create_check_constraint(
        "ck_knowledge_points_parent_not_self",
        "knowledge_points",
        "parent_id IS NULL OR parent_id <> id",
    )

    op.drop_constraint(
        "knowledge_points_chapter_id_fkey",
        "knowledge_points",
        type_="foreignkey",
    )
    op.drop_index("idx_knowledge_points_chapter", table_name="knowledge_points")
    op.drop_constraint(
        "uq_knowledge_points_subject_name",
        "knowledge_points",
        type_="unique",
    )
    op.drop_column("knowledge_points", "chapter_id")
    op.drop_column("knowledge_points", "is_active")

    op.create_foreign_key(
        "knowledge_points_parent_id_fkey",
        "knowledge_points",
        "knowledge_points",
        ["parent_id"],
        ["id"],
        ondelete="RESTRICT",
    )
    op.create_index(
        "idx_knowledge_points_subject_parent_sort",
        "knowledge_points",
        ["subject_id", "parent_id", "sort_order", "id"],
    )
    op.create_index(
        "idx_knowledge_points_parent",
        "knowledge_points",
        ["parent_id"],
    )
    op.create_index(
        "uq_knowledge_points_root_name",
        "knowledge_points",
        ["subject_id", sa.text("lower(name)")],
        unique=True,
        postgresql_where=sa.text("parent_id IS NULL"),
    )
    op.create_index(
        "uq_knowledge_points_child_name",
        "knowledge_points",
        ["subject_id", "parent_id", sa.text("lower(name)")],
        unique=True,
        postgresql_where=sa.text("parent_id IS NOT NULL"),
    )

    if "chapters" in inspector.get_table_names():
        op.drop_index("idx_chapters_subject_sort", table_name="chapters")
        op.drop_table("chapters")


def downgrade() -> None:
    op.create_table(
        "chapters",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("subject_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(150), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.ForeignKeyConstraint(["subject_id"], ["subjects.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("subject_id", "name", name="uq_chapters_subject_name"),
    )
    op.create_index(
        "idx_chapters_subject_sort",
        "chapters",
        ["subject_id", "sort_order", "id"],
    )

    op.add_column(
        "subjects",
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
    )
    op.execute("UPDATE subjects SET is_active = (status = 'active')")
    op.drop_constraint("ck_subjects_status", "subjects", type_="check")
    op.drop_column("subjects", "status")

    op.add_column(
        "knowledge_points",
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
    )
    op.add_column("knowledge_points", sa.Column("chapter_id", sa.Integer(), nullable=True))
    op.execute("UPDATE knowledge_points SET is_active = (status = 'active')")
    op.create_foreign_key(
        "knowledge_points_chapter_id_fkey",
        "knowledge_points",
        "chapters",
        ["chapter_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.drop_index("uq_knowledge_points_child_name", table_name="knowledge_points")
    op.drop_index("uq_knowledge_points_root_name", table_name="knowledge_points")
    op.drop_index("idx_knowledge_points_parent", table_name="knowledge_points")
    op.drop_index("idx_knowledge_points_subject_parent_sort", table_name="knowledge_points")
    op.drop_constraint("knowledge_points_parent_id_fkey", "knowledge_points", type_="foreignkey")
    op.drop_constraint("ck_knowledge_points_parent_not_self", "knowledge_points", type_="check")
    op.drop_constraint("ck_knowledge_points_status", "knowledge_points", type_="check")
    op.drop_column("knowledge_points", "status")
    op.drop_column("knowledge_points", "parent_id")
    op.create_unique_constraint(
        "uq_knowledge_points_subject_name",
        "knowledge_points",
        ["subject_id", "name"],
    )
    op.create_index(
        "idx_knowledge_points_chapter",
        "knowledge_points",
        ["chapter_id"],
    )
