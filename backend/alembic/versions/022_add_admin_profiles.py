"""add private administrator profiles and home preferences

Revision ID: 022
Revises: 021
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "022"
down_revision: str | None = "021"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "admin_profiles",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("display_name", sa.String(length=100), nullable=False),
        sa.Column("identity_title", sa.String(length=100), server_default="", nullable=False),
        sa.Column("signature", sa.String(length=300), server_default="", nullable=False),
        sa.Column("welcome_message", sa.String(length=300), server_default="", nullable=False),
        sa.Column("timezone", sa.String(length=64), server_default="Asia/Shanghai", nullable=False),
        sa.Column(
            "home_preferences",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'{\"show_welcome\": true, \"section_order\": [\"today\", \"activity\", \"stats\", \"storage\"], \"hidden_sections\": []}'::jsonb"),
            nullable=False,
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", name="uq_admin_profiles_user_id"),
    )
def downgrade() -> None:
    bind = op.get_bind()
    count = bind.execute(sa.text("SELECT count(*) FROM admin_profiles")).scalar_one()
    if count:
        raise RuntimeError("Refusing to downgrade while admin profile data exists")
    op.execute("DROP INDEX IF EXISTS idx_admin_profiles_user_id")
    op.drop_table("admin_profiles")
