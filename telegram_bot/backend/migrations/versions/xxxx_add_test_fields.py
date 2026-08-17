"""Add test-specific fields to exams table

Revision ID: add_test_fields
Revises: (oldingi migration ID)
Create Date: 2026-08-16
"""
from alembic import op
import sqlalchemy as sa

revision = 'add_test_fields'
down_revision = None  # O'z migration ID'ngizni qo'ying
branch_labels = None
depends_on = None

def upgrade() -> None:
    # exams jadvaliga yangi ustunlar
    op.add_column('exams', sa.Column('is_published', sa.Boolean(), server_default='false', nullable=False))
    op.add_column('exams', sa.Column('channel_post_id', sa.BigInteger(), nullable=True))
    op.add_column('exams', sa.Column('published_at', sa.DateTime(timezone=True), nullable=True))
    
    # Indexlar
    op.create_index('idx_exams_is_published', 'exams', ['is_published'])
    op.create_index('idx_exams_cefr_published', 'exams', ['cefr_level', 'is_published'])

def downgrade() -> None:
    op.drop_index('idx_exams_cefr_published')
    op.drop_index('idx_exams_is_published')
    op.drop_column('exams', 'published_at')
    op.drop_column('exams', 'channel_post_id')
    op.drop_column('exams', 'is_published')     