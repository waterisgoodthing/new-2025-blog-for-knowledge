"""add canonical question contract beside legacy question fields

Revision ID: 020
Revises: 019
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "020"
down_revision: str | None = "019"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    columns = {column["name"] for column in inspector.get_columns("questions")}

    if "stem_md" not in columns:
        op.add_column("questions", sa.Column("stem_md", sa.Text(), nullable=True))
    if "answer_data" not in columns:
        op.add_column(
            "questions",
            sa.Column("answer_data", sa.JSON(), nullable=False, server_default="{}"),
        )
    if "analysis_md" not in columns:
        op.add_column("questions", sa.Column("analysis_md", sa.Text(), nullable=True))

    op.execute(
        "UPDATE questions SET stem_md = question_text "
        "WHERE stem_md IS NULL"
    )
    op.execute(
        "UPDATE questions SET analysis_md = explanation "
        "WHERE analysis_md IS NULL AND explanation IS NOT NULL"
    )
    op.execute(
        "UPDATE questions SET answer_data = json_build_object(" 
        "'kind', question_type, 'value', correct_answer) "
        "WHERE answer_data::text = '{}' AND correct_answer IS NOT NULL"
    )
    op.alter_column("questions", "stem_md", nullable=False)

    op.drop_constraint("ck_questions_difficulty", "questions", type_="check")
    op.create_check_constraint(
        "ck_questions_difficulty",
        "questions",
        "difficulty IS NULL OR difficulty IN ('unspecified', 'easy', 'medium', 'hard')",
    )

    source_columns = {column["name"] for column in inspector.get_columns("question_sources")}
    if "source_title" not in source_columns:
        op.add_column(
            "question_sources",
            sa.Column("source_title", sa.String(300), nullable=True),
        )
        op.execute(
            "UPDATE question_sources SET source_title = source_name "
            "WHERE source_name IS NOT NULL"
        )
    if "source_url" not in source_columns:
        op.add_column("question_sources", sa.Column("source_url", sa.Text(), nullable=True))
    if "source_note" not in source_columns:
        op.add_column("question_sources", sa.Column("source_note", sa.Text(), nullable=True))
    constraints = {constraint["name"] for constraint in inspector.get_unique_constraints("question_sources")}
    if "uq_question_sources_ref" in constraints:
        op.drop_constraint("uq_question_sources_ref", "question_sources", type_="unique")
    op.alter_column("question_sources", "source_ref", nullable=True)

    if "question_knowledge_points" not in inspector.get_table_names():
        op.create_table(
            "question_knowledge_points",
            sa.Column("question_id", postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column("knowledge_point_id", sa.Integer(), nullable=False),
            sa.Column("role", sa.String(20), nullable=False, server_default="primary"),
            sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.CheckConstraint(
                "role IN ('primary', 'secondary', 'prerequisite')",
                name="ck_question_knowledge_points_role",
            ),
            sa.ForeignKeyConstraint(
                ["question_id"], ["questions.id"],
                name="fk_question_knowledge_points_question", ondelete="CASCADE",
            ),
            sa.ForeignKeyConstraint(
                ["knowledge_point_id"], ["knowledge_points.id"],
                name="fk_question_knowledge_points_knowledge_point", ondelete="CASCADE",
            ),
            sa.PrimaryKeyConstraint("question_id", "knowledge_point_id"),
        )
        op.create_index(
            "idx_question_knowledge_points_question",
            "question_knowledge_points",
            ["question_id", "sort_order"],
        )
        op.create_index(
            "idx_question_knowledge_points_knowledge_point",
            "question_knowledge_points",
            ["knowledge_point_id"],
        )

    invalid_links = bind.execute(
        sa.text(
            "SELECT count(*) FROM knowledge_point_links kpl "
            "JOIN questions q ON q.id::text = kpl.target_id "
            "JOIN knowledge_points kp ON kp.id = kpl.knowledge_point_id "
            "WHERE kpl.target_type = 'question' AND kp.subject_id <> q.subject_id"
        )
    ).scalar_one()
    if invalid_links:
        raise RuntimeError(
            "Cannot migrate cross-subject question Knowledge Point links: "
            f"{invalid_links} rows"
        )
    op.execute(
        "INSERT INTO question_knowledge_points "
        "(question_id, knowledge_point_id, role, sort_order) "
        "SELECT q.id, kpl.knowledge_point_id, 'primary', 0 "
        "FROM knowledge_point_links kpl "
        "JOIN questions q ON q.id::text = kpl.target_id "
        "WHERE kpl.target_type = 'question' "
        "ON CONFLICT (question_id, knowledge_point_id) DO NOTHING"
    )


def downgrade() -> None:
    bind = op.get_bind()
    canonical_count = bind.execute(
        sa.text("SELECT count(*) FROM question_knowledge_points")
    ).scalar_one()
    if canonical_count:
        raise RuntimeError(
            "Refusing to downgrade while canonical Question-KnowledgePoint rows exist"
        )
    op.drop_index("idx_question_knowledge_points_knowledge_point", table_name="question_knowledge_points")
    op.drop_index("idx_question_knowledge_points_question", table_name="question_knowledge_points")
    op.drop_table("question_knowledge_points")
    op.drop_column("question_sources", "source_title")
    op.drop_column("question_sources", "source_url")
    op.drop_column("question_sources", "source_note")
    op.alter_column("question_sources", "source_ref", nullable=False)
    op.drop_constraint("ck_questions_difficulty", "questions", type_="check")
    op.create_check_constraint(
        "ck_questions_difficulty",
        "questions",
        "difficulty IS NULL OR difficulty IN ('easy', 'medium', 'hard')",
    )
    op.drop_column("questions", "analysis_md")
    op.drop_column("questions", "answer_data")
    op.drop_column("questions", "stem_md")
