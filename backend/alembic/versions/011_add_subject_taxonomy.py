"""add subject taxonomy

Revision ID: 011
Revises: 010
Create Date: 2026-07-03
"""

from alembic import op
import sqlalchemy as sa


revision = "011"
down_revision = "010"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("subjects", sa.Column("description", sa.Text(), nullable=True))
    op.add_column(
        "subjects",
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
    )
    op.add_column(
        "subjects",
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
    )
    op.add_column(
        "subjects",
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )
    op.add_column(
        "subjects",
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )

    op.create_table(
        "chapters",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column(
            "subject_id",
            sa.Integer(),
            sa.ForeignKey("subjects.id", ondelete="CASCADE"),
            nullable=False,
        ),
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
        sa.UniqueConstraint(
            "subject_id",
            "name",
            name="uq_chapters_subject_name",
        ),
    )
    op.create_index(
        "idx_chapters_subject_sort",
        "chapters",
        ["subject_id", "sort_order", "id"],
    )

    op.create_table(
        "knowledge_points",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column(
            "subject_id",
            sa.Integer(),
            sa.ForeignKey("subjects.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "chapter_id",
            sa.Integer(),
            sa.ForeignKey("chapters.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("name", sa.String(200), nullable=False),
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
        sa.UniqueConstraint(
            "subject_id",
            "name",
            name="uq_knowledge_points_subject_name",
        ),
    )
    op.create_index(
        "idx_knowledge_points_subject_sort",
        "knowledge_points",
        ["subject_id", "sort_order", "id"],
    )
    op.create_index(
        "idx_knowledge_points_chapter",
        "knowledge_points",
        ["chapter_id"],
    )

    op.create_table(
        "knowledge_point_links",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column(
            "knowledge_point_id",
            sa.Integer(),
            sa.ForeignKey("knowledge_points.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("target_type", sa.String(30), nullable=False),
        sa.Column("target_id", sa.String(64), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.UniqueConstraint(
            "knowledge_point_id",
            "target_type",
            "target_id",
            name="uq_knowledge_point_links_target",
        ),
    )
    op.create_index(
        "idx_knowledge_point_links_target",
        "knowledge_point_links",
        ["target_type", "target_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "idx_knowledge_point_links_target",
        table_name="knowledge_point_links",
    )
    op.drop_table("knowledge_point_links")
    op.drop_index(
        "idx_knowledge_points_chapter",
        table_name="knowledge_points",
    )
    op.drop_index(
        "idx_knowledge_points_subject_sort",
        table_name="knowledge_points",
    )
    op.drop_table("knowledge_points")
    op.drop_index("idx_chapters_subject_sort", table_name="chapters")
    op.drop_table("chapters")
    op.drop_column("subjects", "updated_at")
    op.drop_column("subjects", "created_at")
    op.drop_column("subjects", "sort_order")
    op.drop_column("subjects", "is_active")
    op.drop_column("subjects", "description")
