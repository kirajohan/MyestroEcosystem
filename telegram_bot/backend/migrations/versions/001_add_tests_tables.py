"""Add tests, test_questions, test_attempts tables

Revision ID: 001_add_tests_tables
Revises: 
Create Date: 2026-08-22 19:35:12.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001_add_tests_tables'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create tests table
    op.create_table(
        'tests',
        sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('cefr_level', sa.String(2), nullable=False),
        sa.Column('passing_score', sa.Integer(), nullable=False, server_default='60'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('total_duration', sa.Integer(), nullable=False, server_default='30'),
        sa.Column('max_score', sa.Integer(), nullable=True),
        sa.Column('status', sa.String(50), nullable=False, server_default='active'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_tests_id'), 'tests', ['id'], unique=False)
    op.create_index(op.f('ix_tests_cefr_level'), 'tests', ['cefr_level'], unique=False)

    # Create test_questions table
    op.create_table(
        'test_questions',
        sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
        sa.Column('test_id', sa.Integer(), nullable=False),
        sa.Column('question_text', sa.Text(), nullable=False),
        sa.Column('question_type', sa.String(50), nullable=False, server_default='multiple_choice'),
        sa.Column('options', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('correct_answer', sa.String(500), nullable=False),
        sa.Column('explanation', sa.Text(), nullable=True),
        sa.Column('points', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('difficulty', sa.String(20), nullable=False, server_default='medium'),
        sa.Column('order_index', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['test_id'], ['tests.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_test_questions_id'), 'test_questions', ['id'], unique=False)
    op.create_index(op.f('ix_test_questions_test_id'), 'test_questions', ['test_id'], unique=False)

    # Create test_attempts table
    op.create_table(
        'test_attempts',
        sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
        sa.Column('user_id', sa.BigInteger(), nullable=False),
        sa.Column('test_id', sa.Integer(), nullable=False),
        sa.Column('score', sa.Integer(), nullable=False),
        sa.Column('total_questions', sa.Integer(), nullable=False),
        sa.Column('percentage', sa.Integer(), nullable=False),
        sa.Column('passed', sa.Boolean(), nullable=False),
        sa.Column('finished_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['test_id'], ['tests.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_test_attempts_id'), 'test_attempts', ['id'], unique=False)
    op.create_index(op.f('ix_test_attempts_user_id'), 'test_attempts', ['user_id'], unique=False)
    op.create_index(op.f('ix_test_attempts_test_id'), 'test_attempts', ['test_id'], unique=False)


def downgrade() -> None:
    # Drop test_attempts table
    op.drop_index(op.f('ix_test_attempts_test_id'), table_name='test_attempts')
    op.drop_index(op.f('ix_test_attempts_user_id'), table_name='test_attempts')
    op.drop_index(op.f('ix_test_attempts_id'), table_name='test_attempts')
    op.drop_table('test_attempts')

    # Drop test_questions table
    op.drop_index(op.f('ix_test_questions_test_id'), table_name='test_questions')
    op.drop_index(op.f('ix_test_questions_id'), table_name='test_questions')
    op.drop_table('test_questions')

    # Drop tests table
    op.drop_index(op.f('ix_tests_cefr_level'), table_name='tests')
    op.drop_index(op.f('ix_tests_id'), table_name='tests')
    op.drop_table('tests')
