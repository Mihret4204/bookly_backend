"""Initial schema — creates all tables from scratch.

Revision ID: 748226c992a4
Revises:
Create Date: 2026-07-14 23:47:43.290673

"""
from typing import Sequence, Union

import sqlalchemy as sa
import sqlmodel
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = '748226c992a4'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── tags ──────────────────────────────────────────────────────────────────
    op.create_table(
        'tags',
        sa.Column('uid', sa.UUID(), nullable=False),
        sa.Column('name', sqlmodel.sql.sqltypes.AutoString(length=30), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('uid'),
        sa.UniqueConstraint('uid'),
        sa.UniqueConstraint('name'),
    )

    # ── users ─────────────────────────────────────────────────────────────────
    op.create_table(
        'users',
        sa.Column('uid', sa.UUID(), nullable=False),
        sa.Column('username', sqlmodel.sql.sqltypes.AutoString(length=32), nullable=False),
        sa.Column('email', sqlmodel.sql.sqltypes.AutoString(length=40), nullable=False),
        sa.Column('first_name', sqlmodel.sql.sqltypes.AutoString(length=25), nullable=True),
        sa.Column('last_name', sqlmodel.sql.sqltypes.AutoString(length=25), nullable=True),
        sa.Column('role', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('is_verified', sa.Boolean(), nullable=False),
        sa.Column('password_hash', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('profile_image', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('uid'),
        sa.UniqueConstraint('uid'),
        sa.UniqueConstraint('username'),
        sa.UniqueConstraint('email'),
    )

    # ── books ─────────────────────────────────────────────────────────────────
    # published_date is VARCHAR — the model stores it as a string
    op.create_table(
        'books',
        sa.Column('uid', sa.UUID(), nullable=False),
        sa.Column('title', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('author', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('publisher', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('published_date', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('page_count', sa.Integer(), nullable=False),
        sa.Column('language', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('cover_image_path', sa.VARCHAR(), nullable=True),
        sa.Column('user_uid', sa.UUID(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_uid'], ['users.uid'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('uid'),
        sa.UniqueConstraint('uid'),
    )

    # ── book_tags ─────────────────────────────────────────────────────────────
    op.create_table(
        'book_tags',
        sa.Column('book_uid', sa.UUID(), nullable=False),
        sa.Column('tag_uid', sa.UUID(), nullable=False),
        sa.ForeignKeyConstraint(['book_uid'], ['books.uid'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['tag_uid'], ['tags.uid'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('book_uid', 'tag_uid'),
    )

    # ── reviews ───────────────────────────────────────────────────────────────
    op.create_table(
        'reviews',
        sa.Column('uid', sa.UUID(), nullable=False),
        sa.Column('rating', sa.Integer(), nullable=False),
        sa.Column('review_text', sa.VARCHAR(), nullable=False),
        sa.Column('user_uid', sa.UUID(), nullable=True),
        sa.Column('book_uid', sa.UUID(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['book_uid'], ['books.uid'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_uid'], ['users.uid'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('uid'),
        sa.UniqueConstraint('uid'),
    )

    # ── user_favorites ────────────────────────────────────────────────────────
    op.create_table(
        'user_favorites',
        sa.Column('user_uid', sa.UUID(), nullable=False),
        sa.Column('book_uid', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['book_uid'], ['books.uid'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_uid'], ['users.uid'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('user_uid', 'book_uid'),
    )


def downgrade() -> None:
    # Drop in reverse dependency order
    op.drop_table('user_favorites')
    op.drop_table('reviews')
    op.drop_table('book_tags')
    op.drop_table('books')
    op.drop_table('users')
    op.drop_table('tags')
