"""Add AI memory system tables and columns

Revision ID: ai_memory_001
Revises: (oxirgi revision ID)
Create Date: 2025-08-08 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'ai_memory_001'
down_revision = None  # ← OXIRGI REVISION ID'ni qo'ying (git log orqali tekshiring)
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add AI memory session tracking and context storage."""
    
    # 1. AI Memory Sessions jadval
    op.create_table(
        'ai_memory_sessions',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('user_id', sa.BigInteger(), nullable=False),
        sa.Column('session_id', postgresql.UUID(as_uuid=True), nullable=False, unique=True, server_default=sa.func.gen_random_uuid()),
        sa.Column('title', sa.String(255), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('last_activity_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('message_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('context_summary', sa.Text(), nullable=True),
        sa.Column('summary_generated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('language', sa.String(10), nullable=False, server_default='uz'),
        sa.Column('cefr_level', sa.String(10), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'is_active', name='idx_ai_memory_sessions_user_active')
    )
    
    # Indexes
    op.create_index('idx_ai_memory_sessions_user_id', 'ai_memory_sessions', ['user_id'])
    op.create_index('idx_ai_memory_sessions_expires_at', 'ai_memory_sessions', ['expires_at'])
    op.create_index('idx_ai_memory_sessions_last_activity', 'ai_memory_sessions', ['last_activity_at'], postgresql_using='DESC')
    
    # 2. Messages jadvaliga yangi ustunlar
    op.add_column('messages', 
        sa.Column('session_id', postgresql.UUID(as_uuid=True), nullable=True)
    )
    op.add_column('messages',
        sa.Column('is_in_memory', sa.Boolean(), nullable=False, server_default='true')
    )
    op.add_column('messages',
        sa.Column('memory_index', sa.Integer(), nullable=True)
    )
    
    # Foreign key
    op.create_foreign_key(
        'fk_messages_session_id',
        'messages', 'ai_memory_sessions',
        ['session_id'], ['session_id'],
        ondelete='CASCADE'
    )
    
    # Indexes
    op.create_index('idx_messages_session_id', 'messages', ['session_id'])
    op.create_index('idx_messages_session_created', 'messages', ['session_id', 'created_at'], postgresql_using='DESC')


def downgrade() -> None:
    """Remove AI memory system tables and columns."""
    
    # Messages indexlari o'chirish
    op.drop_index('idx_messages_session_created', table_name='messages')
    op.drop_index('idx_messages_session_id', table_name='messages')
    
    # Foreign key o'chirish
    op.drop_constraint('fk_messages_session_id', 'messages', type_='foreignkey')
    
    # Columns o'chirish
    op.drop_column('messages', 'memory_index')
    op.drop_column('messages', 'is_in_memory')
    op.drop_column('messages', 'session_id')
    
    # ai_memory_sessions jadvalini o'chirish
    op.drop_index('idx_ai_memory_sessions_last_activity', table_name='ai_memory_sessions')
    op.drop_index('idx_ai_memory_sessions_expires_at', table_name='ai_memory_sessions')
    op.drop_index('idx_ai_memory_sessions_user_id', table_name='ai_memory_sessions')
    op.drop_table('ai_memory_sessions')