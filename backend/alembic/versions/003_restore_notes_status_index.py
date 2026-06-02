"""restore notes status index

Revision ID: 003
Revises: 1119bee5a419
Create Date: 2026-06-01

"""
from typing import Sequence, Union

from alembic import op


revision: str = "003"
down_revision: Union[str, None] = "1119bee5a419"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_index("idx_notes_status", "notes", ["status"], unique=False)


def downgrade() -> None:
    op.drop_index("idx_notes_status", table_name="notes")
