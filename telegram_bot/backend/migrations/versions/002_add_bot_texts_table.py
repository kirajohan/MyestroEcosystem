"""Add bot_texts table for CMS

Revision ID: 002_add_bot_texts_table
Revises: 001_add_tests_tables
Create Date: 2024-12-20 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '002_add_bot_texts_table'
down_revision: Union[str, None] = '001_add_tests_tables'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create bot_texts table
    op.create_table(
        'bot_texts',
        sa.Column('id', sa.BigInteger(), nullable=False, autoincrement=True),
        sa.Column('key', sa.String(100), nullable=False, index=True),
        sa.Column('lang', sa.String(10), nullable=False, server_default='uz', index=True),
        sa.Column('text', sa.Text(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('key', 'lang', name='uq_bot_text_key_lang')
    )
    op.create_index(op.f('ix_bot_texts_key'), 'bot_texts', ['key'], unique=False)
    op.create_index(op.f('ix_bot_texts_lang'), 'bot_texts', ['lang'], unique=False)


def downgrade() -> None:
    # Drop bot_texts table
    op.drop_index(op.f('ix_bot_texts_lang'), table_name='bot_texts')
    op.drop_index(op.f('ix_bot_texts_key'), table_name='bot_texts')
    op.drop_table('bot_texts')
