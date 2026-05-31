"""add user admin field

Revision ID: 0ec85724afb9
Revises: 002
Create Date: 2026-05-30 17:41:44.922148

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '0ec85724afb9'
down_revision: Union[str, None] = '002'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('users', sa.Column('is_admin', sa.Boolean(), server_default='false', nullable=False))


def downgrade() -> None:
    op.drop_column('users', 'is_admin')
