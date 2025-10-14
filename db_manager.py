#!/usr/bin/env python3
"""
数据库版本管理工具
使用 Alembic 进行数据库迁移管理
"""

import os
import sys
import argparse
from pathlib import Path
from alembic.config import Config
from alembic import command
from sqlalchemy import create_engine, text
from backend.database import Base, engine as db_engine
from config import Config as AppConfig

# 项目根目录
PROJECT_ROOT = Path(__file__).parent
ALEMBIC_INI = PROJECT_ROOT / "alembic.ini"


class DatabaseManager:
    """数据库管理类"""
    
    def __init__(self):
        """初始化数据库管理器"""
        self.alembic_cfg = Config(str(ALEMBIC_INI))
        self.engine = db_engine
        
    def create_database(self):
        """创建数据库（如果不存在）"""
        try:
            # 连接MySQL服务器（不指定数据库）
            temp_url = f"mysql+pymysql://{AppConfig.MYSQL_USER}:{AppConfig.MYSQL_PASSWORD}@{AppConfig.MYSQL_HOST}:{AppConfig.MYSQL_PORT}"
            temp_engine = create_engine(temp_url)
            
            with temp_engine.connect() as conn:
                # 检查数据库是否存在
                result = conn.execute(text(f"SHOW DATABASES LIKE '{AppConfig.MYSQL_DATABASE}'"))
                if result.fetchone() is None:
                    # 创建数据库
                    conn.execute(text(f"CREATE DATABASE {AppConfig.MYSQL_DATABASE} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"))
                    conn.commit()
                    print(f"✅ 数据库 '{AppConfig.MYSQL_DATABASE}' 创建成功")
                else:
                    print(f"ℹ️  数据库 '{AppConfig.MYSQL_DATABASE}' 已存在")
            
            temp_engine.dispose()
            return True
        except Exception as e:
            print(f"❌ 创建数据库失败: {e}")
            return False
    
    def drop_database(self):
        """删除数据库（谨慎使用！）"""
        confirm = input(f"⚠️  确定要删除数据库 '{AppConfig.MYSQL_DATABASE}' 吗？这将删除所有数据！(yes/no): ")
        if confirm.lower() != 'yes':
            print("已取消删除操作")
            return False
        
        try:
            temp_url = f"mysql+pymysql://{AppConfig.MYSQL_USER}:{AppConfig.MYSQL_PASSWORD}@{AppConfig.MYSQL_HOST}:{AppConfig.MYSQL_PORT}"
            temp_engine = create_engine(temp_url)
            
            with temp_engine.connect() as conn:
                conn.execute(text(f"DROP DATABASE IF EXISTS {AppConfig.MYSQL_DATABASE}"))
                conn.commit()
                print(f"✅ 数据库 '{AppConfig.MYSQL_DATABASE}' 已删除")
            
            temp_engine.dispose()
            return True
        except Exception as e:
            print(f"❌ 删除数据库失败: {e}")
            return False
    
    def init_db(self):
        """初始化数据库（创建数据库并运行迁移）"""
        print("开始初始化数据库...")
        
        # 1. 创建数据库
        if not self.create_database():
            return False
        
        # 2. 运行迁移到最新版本
        print("\n运行数据库迁移...")
        return self.upgrade()
    
    def upgrade(self, revision='head'):
        """升级数据库到指定版本"""
        try:
            print(f"升级数据库到版本: {revision}")
            command.upgrade(self.alembic_cfg, revision)
            print("✅ 数据库升级成功")
            return True
        except Exception as e:
            print(f"❌ 数据库升级失败: {e}")
            return False
    
    def downgrade(self, revision='-1'):
        """降级数据库到指定版本"""
        try:
            print(f"降级数据库到版本: {revision}")
            command.downgrade(self.alembic_cfg, revision)
            print("✅ 数据库降级成功")
            return True
        except Exception as e:
            print(f"❌ 数据库降级失败: {e}")
            return False
    
    def current(self):
        """显示当前数据库版本"""
        try:
            print("当前数据库版本:")
            command.current(self.alembic_cfg)
            return True
        except Exception as e:
            print(f"❌ 获取当前版本失败: {e}")
            return False
    
    def history(self):
        """显示迁移历史"""
        try:
            print("数据库迁移历史:")
            command.history(self.alembic_cfg)
            return True
        except Exception as e:
            print(f"❌ 获取迁移历史失败: {e}")
            return False
    
    def revision(self, message, autogenerate=True):
        """创建新的迁移版本"""
        try:
            print(f"创建新的迁移版本: {message}")
            if autogenerate:
                command.revision(self.alembic_cfg, message=message, autogenerate=True)
            else:
                command.revision(self.alembic_cfg, message=message)
            print("✅ 迁移脚本创建成功")
            return True
        except Exception as e:
            print(f"❌ 创建迁移脚本失败: {e}")
            return False
    
    def stamp(self, revision):
        """标记数据库为指定版本（不运行迁移）"""
        try:
            print(f"标记数据库版本为: {revision}")
            command.stamp(self.alembic_cfg, revision)
            print("✅ 数据库版本标记成功")
            return True
        except Exception as e:
            print(f"❌ 标记版本失败: {e}")
            return False
    
    def reset_db(self):
        """重置数据库（删除并重新创建）"""
        print("⚠️  重置数据库将删除所有数据！")
        if self.drop_database():
            return self.init_db()
        return False
    
    def check_connection(self):
        """检查数据库连接"""
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text("SELECT 1"))
                result.fetchone()
            print("✅ 数据库连接正常")
            print(f"数据库地址: {AppConfig.MYSQL_HOST}:{AppConfig.MYSQL_PORT}")
            print(f"数据库名称: {AppConfig.MYSQL_DATABASE}")
            print(f"用户名: {AppConfig.MYSQL_USER}")
            return True
        except Exception as e:
            print(f"❌ 数据库连接失败: {e}")
            return False


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='数据库版本管理工具')
    parser.add_argument('command', help='命令',
                       choices=['init', 'upgrade', 'downgrade', 'current', 'history', 
                               'revision', 'stamp', 'reset', 'check', 'create', 'drop'])
    parser.add_argument('-m', '--message', help='迁移消息（用于revision命令）')
    parser.add_argument('-r', '--revision', help='版本号（用于upgrade/downgrade/stamp命令）', 
                       default='head')
    parser.add_argument('--no-autogenerate', action='store_true', 
                       help='不自动生成迁移（用于revision命令）')
    
    args = parser.parse_args()
    
    db_manager = DatabaseManager()
    
    # 执行相应的命令
    if args.command == 'init':
        db_manager.init_db()
    elif args.command == 'upgrade':
        db_manager.upgrade(args.revision)
    elif args.command == 'downgrade':
        db_manager.downgrade(args.revision)
    elif args.command == 'current':
        db_manager.current()
    elif args.command == 'history':
        db_manager.history()
    elif args.command == 'revision':
        if not args.message:
            print("❌ 请使用 -m 参数提供迁移消息")
            sys.exit(1)
        db_manager.revision(args.message, not args.no_autogenerate)
    elif args.command == 'stamp':
        db_manager.stamp(args.revision)
    elif args.command == 'reset':
        db_manager.reset_db()
    elif args.command == 'check':
        db_manager.check_connection()
    elif args.command == 'create':
        db_manager.create_database()
    elif args.command == 'drop':
        db_manager.drop_database()


if __name__ == '__main__':
    main()

