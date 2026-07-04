"""change folder parent_id ondelete from CASCADE to SET NULL

Revision ID: 007
Revises: 006
Create Date: 2026-06-08
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision = "007"
down_revision = "006"
branch_labels = None
depends_on = None


def _folder_parent_fk() -> dict | None:
    for foreign_key in sa.inspect(op.get_bind()).get_foreign_keys("folders"):
        if foreign_key.get("constrained_columns") == ["parent_id"]:
            return foreign_key
    return None


def upgrade() -> None:
    foreign_key = _folder_parent_fk()
    if foreign_key and (foreign_key.get("options") or {}).get("ondelete") == "SET NULL":
        return
    if foreign_key:
        op.drop_constraint(foreign_key["name"], "folders", type_="foreignkey")
    op.create_foreign_key(
        "folders_parent_id_fkey",
        "folders",
        "folders",
        ["parent_id"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    foreign_key = _folder_parent_fk()
    if foreign_key and (foreign_key.get("options") or {}).get("ondelete") == "CASCADE":
        return
    if foreign_key:
        op.drop_constraint(foreign_key["name"], "folders", type_="foreignkey")
    op.create_foreign_key(
        "folders_parent_id_fkey",
        "folders",
        "folders",
        ["parent_id"],
        ["id"],
        ondelete="CASCADE",
    )
