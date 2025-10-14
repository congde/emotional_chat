"""add response evaluation table

Revision ID: 002
Revises: 001
Create Date: 2025-10-14

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade():
    """创建response_evaluations表"""
    op.create_table(
        'response_evaluations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('session_id', sa.String(100), nullable=True),
        sa.Column('user_id', sa.String(100), nullable=True),
        sa.Column('message_id', sa.BigInteger(), nullable=True),
        
        # 评估对象
        sa.Column('user_message', sa.Text(), nullable=True),
        sa.Column('bot_response', sa.Text(), nullable=True),
        sa.Column('user_emotion', sa.String(50), nullable=True),
        sa.Column('emotion_intensity', sa.Float(), nullable=True),
        
        # 评估维度分数 (1-5)
        sa.Column('empathy_score', sa.Float(), nullable=True),
        sa.Column('naturalness_score', sa.Float(), nullable=True),
        sa.Column('safety_score', sa.Float(), nullable=True),
        
        # 总分和平均分
        sa.Column('total_score', sa.Float(), nullable=True),
        sa.Column('average_score', sa.Float(), nullable=True),
        
        # 评估详情 (JSON格式)
        sa.Column('empathy_reasoning', sa.Text(), nullable=True),
        sa.Column('naturalness_reasoning', sa.Text(), nullable=True),
        sa.Column('safety_reasoning', sa.Text(), nullable=True),
        sa.Column('overall_comment', sa.Text(), nullable=True),
        sa.Column('strengths', sa.Text(), nullable=True),
        sa.Column('weaknesses', sa.Text(), nullable=True),
        sa.Column('improvement_suggestions', sa.Text(), nullable=True),
        
        # 元数据
        sa.Column('evaluation_model', sa.String(100), nullable=True),
        sa.Column('prompt_version', sa.String(50), nullable=True),
        sa.Column('is_human_verified', sa.Boolean(), nullable=True, default=False),
        sa.Column('human_rating_diff', sa.Float(), nullable=True),
        
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        
        sa.PrimaryKeyConstraint('id')
    )
    
    # 创建索引
    op.create_index('ix_response_evaluations_session_id', 'response_evaluations', ['session_id'])
    op.create_index('ix_response_evaluations_user_id', 'response_evaluations', ['user_id'])
    op.create_index('ix_response_evaluations_message_id', 'response_evaluations', ['message_id'])
    op.create_index('ix_response_evaluations_id', 'response_evaluations', ['id'])


def downgrade():
    """删除response_evaluations表"""
    op.drop_index('ix_response_evaluations_message_id', table_name='response_evaluations')
    op.drop_index('ix_response_evaluations_user_id', table_name='response_evaluations')
    op.drop_index('ix_response_evaluations_session_id', table_name='response_evaluations')
    op.drop_index('ix_response_evaluations_id', table_name='response_evaluations')
    op.drop_table('response_evaluations')

