"""Initial schema

Revision ID: 001
Revises: 
Create Date: 2025-10-14 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """创建所有初始表"""
    
    # 创建 users 表
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
        sa.Column('user_id', sa.String(length=100), nullable=True),
        sa.Column('username', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    op.create_index(op.f('ix_users_user_id'), 'users', ['user_id'], unique=True)
    
    # 创建 chat_sessions 表
    op.create_table(
        'chat_sessions',
        sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
        sa.Column('session_id', sa.String(length=100), nullable=True),
        sa.Column('user_id', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_chat_sessions_id'), 'chat_sessions', ['id'], unique=False)
    op.create_index(op.f('ix_chat_sessions_session_id'), 'chat_sessions', ['session_id'], unique=True)
    op.create_index(op.f('ix_chat_sessions_user_id'), 'chat_sessions', ['user_id'], unique=False)
    
    # 创建 chat_messages 表
    op.create_table(
        'chat_messages',
        sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
        sa.Column('session_id', sa.String(length=100), nullable=True),
        sa.Column('user_id', sa.String(length=100), nullable=True),
        sa.Column('role', sa.String(length=20), nullable=True),
        sa.Column('content', sa.Text(), nullable=True),
        sa.Column('emotion', sa.String(length=50), nullable=True),
        sa.Column('emotion_intensity', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_chat_messages_id'), 'chat_messages', ['id'], unique=False)
    op.create_index(op.f('ix_chat_messages_session_id'), 'chat_messages', ['session_id'], unique=False)
    op.create_index(op.f('ix_chat_messages_user_id'), 'chat_messages', ['user_id'], unique=False)
    
    # 创建 emotion_analysis 表
    op.create_table(
        'emotion_analysis',
        sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
        sa.Column('session_id', sa.String(length=100), nullable=True),
        sa.Column('user_id', sa.String(length=100), nullable=True),
        sa.Column('message_id', sa.Integer(), nullable=True),
        sa.Column('emotion', sa.String(length=50), nullable=True),
        sa.Column('intensity', sa.Float(), nullable=True),
        sa.Column('keywords', sa.Text(), nullable=True),
        sa.Column('suggestions', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_emotion_analysis_id'), 'emotion_analysis', ['id'], unique=False)
    op.create_index(op.f('ix_emotion_analysis_session_id'), 'emotion_analysis', ['session_id'], unique=False)
    op.create_index(op.f('ix_emotion_analysis_user_id'), 'emotion_analysis', ['user_id'], unique=False)
    
    # 创建 knowledge 表
    op.create_table(
        'knowledge',
        sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
        sa.Column('title', sa.String(length=200), nullable=True),
        sa.Column('content', sa.Text(), nullable=True),
        sa.Column('category', sa.String(length=100), nullable=True),
        sa.Column('tags', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_knowledge_id'), 'knowledge', ['id'], unique=False)
    
    # 创建 system_logs 表
    op.create_table(
        'system_logs',
        sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
        sa.Column('level', sa.String(length=20), nullable=True),
        sa.Column('message', sa.Text(), nullable=True),
        sa.Column('session_id', sa.String(length=100), nullable=True),
        sa.Column('user_id', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_system_logs_id'), 'system_logs', ['id'], unique=False)
    op.create_index(op.f('ix_system_logs_session_id'), 'system_logs', ['session_id'], unique=False)
    op.create_index(op.f('ix_system_logs_user_id'), 'system_logs', ['user_id'], unique=False)
    
    # 创建 user_feedback 表
    op.create_table(
        'user_feedback',
        sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
        sa.Column('session_id', sa.String(length=100), nullable=True),
        sa.Column('user_id', sa.String(length=100), nullable=True),
        sa.Column('message_id', sa.Integer(), nullable=True),
        sa.Column('feedback_type', sa.String(length=50), nullable=True),
        sa.Column('rating', sa.Integer(), nullable=True),
        sa.Column('comment', sa.Text(), nullable=True),
        sa.Column('user_message', sa.Text(), nullable=True),
        sa.Column('bot_response', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('is_resolved', sa.Boolean(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_feedback_id'), 'user_feedback', ['id'], unique=False)
    op.create_index(op.f('ix_user_feedback_session_id'), 'user_feedback', ['session_id'], unique=False)
    op.create_index(op.f('ix_user_feedback_user_id'), 'user_feedback', ['user_id'], unique=False)
    op.create_index(op.f('ix_user_feedback_message_id'), 'user_feedback', ['message_id'], unique=False)


def downgrade() -> None:
    """删除所有表"""
    op.drop_index(op.f('ix_user_feedback_message_id'), table_name='user_feedback')
    op.drop_index(op.f('ix_user_feedback_user_id'), table_name='user_feedback')
    op.drop_index(op.f('ix_user_feedback_session_id'), table_name='user_feedback')
    op.drop_index(op.f('ix_user_feedback_id'), table_name='user_feedback')
    op.drop_table('user_feedback')
    
    op.drop_index(op.f('ix_system_logs_user_id'), table_name='system_logs')
    op.drop_index(op.f('ix_system_logs_session_id'), table_name='system_logs')
    op.drop_index(op.f('ix_system_logs_id'), table_name='system_logs')
    op.drop_table('system_logs')
    
    op.drop_index(op.f('ix_knowledge_id'), table_name='knowledge')
    op.drop_table('knowledge')
    
    op.drop_index(op.f('ix_emotion_analysis_user_id'), table_name='emotion_analysis')
    op.drop_index(op.f('ix_emotion_analysis_session_id'), table_name='emotion_analysis')
    op.drop_index(op.f('ix_emotion_analysis_id'), table_name='emotion_analysis')
    op.drop_table('emotion_analysis')
    
    op.drop_index(op.f('ix_chat_messages_user_id'), table_name='chat_messages')
    op.drop_index(op.f('ix_chat_messages_session_id'), table_name='chat_messages')
    op.drop_index(op.f('ix_chat_messages_id'), table_name='chat_messages')
    op.drop_table('chat_messages')
    
    op.drop_index(op.f('ix_chat_sessions_user_id'), table_name='chat_sessions')
    op.drop_index(op.f('ix_chat_sessions_session_id'), table_name='chat_sessions')
    op.drop_index(op.f('ix_chat_sessions_id'), table_name='chat_sessions')
    op.drop_table('chat_sessions')
    
    op.drop_index(op.f('ix_users_user_id'), table_name='users')
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_table('users')

