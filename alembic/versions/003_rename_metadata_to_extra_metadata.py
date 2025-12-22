"""rename metadata to extra_metadata

Revision ID: 003
Revises: 002
Create Date: 2025-01-15 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """将 ab_test_experiments 表中的 metadata 列重命名为 extra_metadata"""
    
    # 检查表是否存在
    connection = op.get_bind()
    inspector = sa.inspect(connection)
    tables = inspector.get_table_names()
    
    if 'ab_test_experiments' not in tables:
        # 表不存在，创建表时使用正确的列名
        op.create_table(
            'ab_test_experiments',
            sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
            sa.Column('experiment_id', sa.String(length=100), nullable=True),
            sa.Column('name', sa.String(length=200), nullable=True),
            sa.Column('description', sa.Text(), nullable=True),
            sa.Column('groups', sa.Text(), nullable=True),
            sa.Column('weights', sa.Text(), nullable=True),
            sa.Column('start_date', sa.DateTime(), nullable=True),
            sa.Column('end_date', sa.DateTime(), nullable=True),
            sa.Column('enabled', sa.Boolean(), nullable=True),
            sa.Column('extra_metadata', sa.Text(), nullable=True),  # 使用正确的列名
            sa.Column('created_at', sa.DateTime(), nullable=True),
            sa.Column('updated_at', sa.DateTime(), nullable=True),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index(op.f('ix_ab_test_experiments_id'), 'ab_test_experiments', ['id'], unique=False)
        op.create_index(op.f('ix_ab_test_experiments_experiment_id'), 'ab_test_experiments', ['experiment_id'], unique=True)
    else:
        # 表存在，检查列是否存在并重命名
        columns = [col['name'] for col in inspector.get_columns('ab_test_experiments')]
        
        if 'metadata' in columns and 'extra_metadata' not in columns:
            # 使用 MySQL 的 ALTER TABLE ... CHANGE COLUMN 语法
            op.execute("ALTER TABLE ab_test_experiments CHANGE COLUMN metadata extra_metadata TEXT")
        elif 'extra_metadata' in columns:
            # 列已经是正确的名称，无需操作
            pass
        elif 'metadata' not in columns:
            # 列不存在，添加新列
            op.add_column('ab_test_experiments', sa.Column('extra_metadata', sa.Text(), nullable=True))


def downgrade() -> None:
    """将 extra_metadata 列重命名回 metadata"""
    connection = op.get_bind()
    inspector = sa.inspect(connection)
    
    if 'ab_test_experiments' in inspector.get_table_names():
        columns = [col['name'] for col in inspector.get_columns('ab_test_experiments')]
        
        if 'extra_metadata' in columns and 'metadata' not in columns:
            # 使用 MySQL 的 ALTER TABLE ... CHANGE COLUMN 语法
            op.execute("ALTER TABLE ab_test_experiments CHANGE COLUMN extra_metadata metadata TEXT")

