"""initial schema

Revision ID: 001
Revises:
Create Date: 2026-05-28

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('username', sa.String(100), unique=True, nullable=False),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
    )

    op.create_table(
        'tags',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('name', sa.String(100), unique=True, nullable=False),
    )

    op.create_table(
        'subjects',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('name', sa.String(100), unique=True, nullable=False),
    )

    op.create_table(
        'categories',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('name', sa.String(100), unique=True, nullable=False),
        sa.Column('sort_order', sa.Integer(), server_default='0'),
    )

    op.create_table(
        'notes',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('slug', sa.String(255), unique=True, nullable=False, index=True),
        sa.Column('title', sa.String(500), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('type', sa.String(20), nullable=False, index=True),
        sa.Column('hidden', sa.Boolean(), server_default='false'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('summary', sa.Text(), nullable=True),
        sa.Column('cover', sa.String(500), nullable=True),
        sa.Column('category', sa.String(100), nullable=True),
        sa.Column('subject', sa.String(100), nullable=True),
        sa.Column('difficulty', sa.String(20), nullable=True),
        sa.Column('question', sa.Text(), nullable=True),
        sa.Column('my_answer', sa.Text(), nullable=True),
        sa.Column('correct_answer', sa.Text(), nullable=True),
        sa.Column('analysis', sa.Text(), nullable=True),
        sa.Column('knowledge_points', sa.Text(), nullable=True),
        sa.Column('ef', sa.Float(), server_default='2.5'),
        sa.Column('interval', sa.Integer(), server_default='0'),
        sa.Column('repetitions', sa.Integer(), server_default='0'),
        sa.Column('next_review', sa.Date(), nullable=True),
        sa.Column('last_reviewed', sa.DateTime(), nullable=True),
        sa.Column('search_vector', postgresql.TSVECTOR(), nullable=True),
    )
    op.create_index('idx_notes_next_review', 'notes', ['next_review'], postgresql_where="type = 'mistake'")
    op.create_index('idx_notes_search', 'notes', ['search_vector'], postgresql_using='gin')

    op.create_table(
        'note_tags',
        sa.Column('note_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('notes.id', ondelete='CASCADE'), primary_key=True),
        sa.Column('tag_id', sa.Integer(), sa.ForeignKey('tags.id', ondelete='CASCADE'), primary_key=True),
    )

    op.create_table(
        'music_items',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('title', sa.String(500), nullable=False),
        sa.Column('artist', sa.String(200), nullable=True),
        sa.Column('artwork', sa.String(500), nullable=True),
        sa.Column('apple_music_url', sa.String(500), nullable=False),
        sa.Column('preview_url', sa.String(500), nullable=True),
        sa.Column('track_id', sa.Integer(), nullable=True),
        sa.Column('sort_order', sa.Integer(), server_default='0'),
        sa.Column('is_active', sa.Boolean(), server_default='true'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
    )

    op.create_table(
        'recommendations',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('date', sa.Date(), unique=True, nullable=False, index=True),
        sa.Column('title', sa.String(500), nullable=False),
        sa.Column('type', sa.String(20), nullable=False),
        sa.Column('reason', sa.Text(), nullable=False),
        sa.Column('target', sa.String(500), nullable=True),
        sa.Column('action_label', sa.String(100), nullable=True),
        sa.Column('source', sa.String(200), nullable=True),
        sa.Column('raw_context', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table('recommendations')
    op.drop_table('music_items')
    op.drop_table('note_tags')
    op.drop_index('idx_notes_search', table_name='notes')
    op.drop_index('idx_notes_next_review', table_name='notes')
    op.drop_table('notes')
    op.drop_table('categories')
    op.drop_table('subjects')
    op.drop_table('tags')
    op.drop_table('users')
