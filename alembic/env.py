#!/usr/bin/env python3
"""Alembic环境配置文件"""

from logging.config import fileConfig
import os
import sys
from pathlib import Path

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent))

# 导入配置和数据库模型
from config import Config
from backend.database import Base

# 这是Alembic配置对象，提供了alembic.ini文件的访问
config = context.config

# 从config.py读取数据库URL，覆盖alembic.ini中的配置
database_url = os.getenv("DATABASE_URL", 
                        f"mysql+pymysql://{Config.MYSQL_USER}:{Config.MYSQL_PASSWORD}@{Config.MYSQL_HOST}:{Config.MYSQL_PORT}/{Config.MYSQL_DATABASE}")
config.set_main_option("sqlalchemy.url", database_url)

# 解释Python日志配置文件
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# 添加你的模型的MetaData对象，用于'autogenerate'支持
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = Base.metadata

# 其他需要从myapp导入的值
# ... 例如：
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata


def run_migrations_offline() -> None:
    """在'离线'模式下运行迁移。
    
    这将配置上下文仅使用URL，而不是Engine，
    尽管在这里也可以接受一个Engine。
    通过跳过Engine创建，我们甚至不需要DBAPI可用。
    
    这里调用context.execute()会将给定的字符串输出到脚本输出。
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """在'在线'模式下运行迁移。
    
    在这种情况下，我们需要创建一个Engine
    并将连接与上下文关联。
    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, 
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

